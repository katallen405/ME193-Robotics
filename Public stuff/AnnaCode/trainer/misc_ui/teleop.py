"""Controller teleoperation for the Trainer (PyScript glue).

Tick-by-tick mapping from joystick to motor command lives in teleop_logic.py
(pure, unit-tested). This file connects it to the page:

  * "Drive with controller" arms a loop that sends the joystick commands to
    whatever motor channels the Output nodes point at, so you can steer the robot.
  * Collect (dataset_ui.py) records those *commanded* values as the labels, which is
    behavior cloning from a human demonstrator.
  * While the network is Running, a stick push overrides it (loop_network in main.py)
    and the human's command is logged as a new row (DAgger, dataset_ui.log_human_row).
"""
import asyncio

import state
from state import get_id
import Device
import teleop_logic as tl

TICK_S = 0.05        # same rate as the Run loop
RESEND_TICKS = 10    # re-send an unchanged command every 0.5 s in case a Bluetooth write was dropped

_generation = 0      # bumped on every arm/disarm so a stale loop exits instead of doubling up


# ── Page settings and devices ────────────────────────────────────────────────

def find_controller():
    """First connected device that reports joystick channels (a Controller, or the virtual one)."""
    for dev in state.devices:
        dev_state = getattr(dev, "state", None)
        if isinstance(dev_state, dict) and "LeftPercent" in dev_state:
            return dev
    return None

def settings() -> dict:
    def number(elem_id, default):
        el = get_id(elem_id)
        try:
            return float(el.value) if el and str(el.value).strip() != "" else default
        except (ValueError, TypeError):
            return default

    def checked(elem_id, default=False):
        el = get_id(elem_id)
        return bool(el.checked) if el else default

    return {
        "max_speed": number("teleop-max", tl.DEFAULT_MAX_SPEED),
        "reverse": checked("teleop-reverse"),
        "log": checked("teleop-log", True),
    }

def output_target(oid: int) -> tuple[str, str]:
    dev_el = get_id(f"dev-output-{oid}")
    chan_el = get_id(f"chan-output-{oid}")
    return (dev_el.value if dev_el else ""), (chan_el.value if chan_el else "")

def _output_channels() -> dict:
    return {out["id"]: output_target(out["id"])[1] for out in state.outputs}


# ── Commands ─────────────────────────────────────────────────────────────────

def _sticks_and_settings():
    ctrl = find_controller()
    if ctrl is None:
        return None
    left, right = tl.stick_values(ctrl.state)
    return ctrl, left, right, settings()

def current_commands() -> dict:
    """{output id: command} the joysticks give right now (drive outputs only); {} with no controller."""
    got = _sticks_and_settings()
    if got is None:
        return {}
    _, left, right, s = got
    return tl.commands_for_outputs(_output_channels(), left, right, s["max_speed"], s["reverse"])

def current_override():
    """Commands to use instead of the network's, or None when the human isn't driving.
    A human is driving when teleop is armed and either stick is pushed past the deadband."""
    if not state.teleop_armed:
        return None
    got = _sticks_and_settings()
    if got is None:
        return None
    _, left, right, s = got
    if not tl.is_deflected(left, right):
        return None
    return tl.commands_for_outputs(_output_channels(), left, right, s["max_speed"], s["reverse"]) or None

def labels_for_collect() -> dict:
    """Labels for Collect: the commanded values, but only while teleop is armed."""
    return current_commands() if state.teleop_armed else {}

def send(cmds: dict):
    """Send commands to the output devices, skipping repeats of an unchanged value."""
    for oid, value in cmds.items():
        dev_name, channel = output_target(oid)
        key = (dev_name, channel)
        last = state.teleop_sent.get(key)
        if last is not None and last[0] == value and last[1] < RESEND_TICKS:
            state.teleop_sent[key] = (value, last[1] + 1)
            continue
        Device.run_output(channel, dev_name, value)
        state.teleop_sent[key] = (value, 0)

def reset_send_cache():
    """Forget what was last sent (call when something else may have changed the motors)."""
    state.teleop_sent.clear()


# ── Arm / disarm ─────────────────────────────────────────────────────────────

def set_status(text: str):
    el = get_id("teleop-status")
    if el:
        el.textContent = text

def _status_text() -> str:
    ctrl = find_controller()
    if ctrl is None:
        return "No controller found. Connect one (or open this page with ?virtual to use the on-screen sticks)."
    left, right = tl.stick_values(ctrl.state)
    text = f"{ctrl.name}: left {left:.0f}, right {right:.0f}"
    if state.is_running and current_override():
        text += "  - you are driving"
    return text

async def _loop(generation: int):
    while state.teleop_armed and generation == _generation:
        if not state.is_running:          # while Running, loop_network owns the motors
            send(current_commands())
        set_status(_status_text())
        await asyncio.sleep(TICK_S)

def arm():
    global _generation
    if state.teleop_armed:
        return
    _generation += 1
    state.teleop_armed = True
    reset_send_cache()
    asyncio.ensure_future(_loop(_generation))

def disarm():
    global _generation
    _generation += 1
    state.teleop_armed = False
    reset_send_cache()
    set_status("")
    if state.is_running:
        return
    for out in state.outputs:             # leave the robot stopped
        dev_name, channel = output_target(out["id"])
        if channel in tl.DRIVE_CHANNELS:
            dev = Device.device_by_name(dev_name)
            try:
                if dev:
                    dev.stop()
            except Exception as e:
                print("Teleop could not stop " + dev_name + ": " + str(e))
