# AnnaCode

Two browser pages for building small neural networks and connecting them to
LEGO Education hardware (motors, color sensor, controller). Nothing to
install: Python runs in the page via [PyScript](https://pyscript.net).

| Page | What it does | Open |
|---|---|---|
| **Builder** (`index.html`) | Wire sensors into a network by hand and set the weights yourself. Outputs drive motors, lights and the beeper. | [Open](https://chrisbuerginrogers.github.io/ME193-Robotics/Public%20stuff/AnnaCode/) |
| **Trainer** (`trainer.html`) | The same tool plus a dataset and training: collect examples from your hardware, train the network, and watch the fit and loss plots. | [Open](https://chrisbuerginrogers.github.io/ME193-Robotics/Public%20stuff/AnnaCode/trainer.html) |

## What you need

- **Chrome or Edge.** Connecting to hardware uses Web Bluetooth, which Safari
  and Firefox don't have. (The trainer still works there with its on-screen
  virtual controller and motor.)
- A LEGO Education hub that is switched on. Turn off other apps connected to
  it first; a hub only talks to one at a time.
- The first load takes a while (the browser downloads Python and numpy).

## Using it

1. Click **Connect device**, pick the hub in the Bluetooth chooser, and click
   **Pair**. The hub beeps when it connects.
2. The device appears in the Devices list, labelled with its card color, for
   example `🟦    Single Motor`. Connect as many as you like.
3. Add inputs, layers and outputs. On each input or output pick a device and a
   channel (for example `Reflection` on a Color Sensor, or `Speed` on a motor).
   The small number beside the device dropdown is that channel's current value.
4. Press the **play** button (▶) to start the network driving the outputs, and the
   stop button (■) to stop it.
5. *Trainer only:* press **Collect** to record rows from the connected inputs and
   outputs into the training data, then **Step** (one epoch) or **Train 50 epochs**.
   **Randomize weights** starts the network over.

Picking a hub that is already connected shows an alert and does nothing.

## Teaching by joystick (Trainer)

Connect a LEGO **Controller** as well as the motor and color sensor, and the
Trainer's **Training data** card gets a *Drive with controller* checkbox. This is
behavior cloning with a human demonstrator, using the controller as the teacher:

1. Set the Output nodes to the motor channels the network should drive (for a
   two-wheeled car: `LeftSpeed` and `RightSpeed`) and the Input node to the
   sensor (for example `Reflection`).
2. Tick **Drive with controller**. The left stick drives the left wheel and the
   right stick drives the right wheel (tank drive); with a single output, whichever
   stick you push harder drives it. **Max speed** caps a full push, and **Reverse**
   flips the direction if forward reads backward.
3. Press **Collect** and drive the robot. Each row is the sensor reading and what
   you *commanded*, not the motor's measured speed, so there is no lag in the labels.
4. **Train 50 epochs**, then press **Run**: the network drives.
5. While it runs, **push a stick to take over.** Your command replaces the network's
   and is added to the data as a new row at that sensor reading (the DAgger idea:
   correct the learner where it actually goes). Release and the network resumes.
   Untick *Add my corrections while running* to take over without recording.
   Retrain on the larger dataset and run again.

Light and beep outputs are never driven by the sticks. With the checkbox off,
Collect behaves as before (it records the measured value).

No controller? Add a virtual one (next section). If both a real and a virtual
controller are connected, the first one in the Devices list is used (the status line
under the checkboxes names it).

The joystick-to-motor mapping is `trainer/network/teleop_logic.py` and its tests
run with plain Python from this folder: `python3 -m unittest discover tests -v`.
The wiring is `trainer/misc_ui/teleop.py`. The right wheel is sign-flipped to match
the example networks (opposite signs for the two wheels go straight); if your robot
drives backward, tick **Reverse**.

## No kit with you? Virtual devices (Trainer)

In the Devices card, pick a device from **Choose a virtual device…** and press **Add**.
A card for it appears (with a short "Added ..." confirmation next to the button) and it
shows up in every Input and Output dropdown. It behaves like the real one. Use as many
as you like, mixed with real hardware or on their own (no Bluetooth needed, so it also
works in Safari and Firefox). The **×** on a card removes it.

| Virtual device | Channels it shows | Notes |
|---|---|---|
| Controller | `LeftPercent`, `RightPercent` | Two sliders, plus the keyboard (below) |
| Double Motor | `LeftSpeed`, `RightSpeed`, `BothSpeed`, `LeftPosition`, `RightPosition`, `LeftAngle`, `RightAngle`, `LeftPower`, `RightPower` | Wheels are mirrored like the real chassis. Outputs: `LeftSpeed`, `RightSpeed`, `BothSpeed` |
| Single Motor | `Speed`, `Position`, `Angle`, `Power` | Output: `Speed` |
| Color Sensor | `Reflection` | Slide it to change what the sensor "sees" (0 dark, 100 bright) |

**Keyboard for the virtual controller** (works whenever you are not typing in a box;
Cmd/Ctrl shortcuts are left alone):

- **Arrow keys** drive like a car: up/down = both sticks forward/back, left/right = turn.
- **W / S** = left stick up/down, **I / K** = right stick up/down.
- The sticks ease out while a key is held and spring back when you let go.

With a virtual controller you can do the whole loop at home: add a controller, a color
sensor and a motor, tick **Drive with controller**, **Collect** while you slide the
sensor and drive with the keys, train, and **Run**.

Virtual devices only have the channels listed above (a real device reports more, such
as the IMU and color channels). Their logic is `trainer/misc_ui/virtual_devices.py`,
with the numbers in `trainer/network/virtual_logic.py` (unit-tested).
`trainer.html?virtual` still works and shows the older single combined controller
and motor panel.

## Troubleshooting

- **A device chip turns red and says "Disconnected" or "No signal" (Trainer).**
  *Disconnected* means the browser reported that the Bluetooth link dropped, for example
  the laptop went to sleep, the device ran out of power, or it moved out of range. While
  a device is disconnected the page stops sending it commands, ignores a disconnected
  controller's sticks (they would otherwise stay stuck at their last value), and stops
  **Run** or **Collect** if an input or output in use has dropped. *No signal* means the
  page has heard nothing for several seconds but the browser has not reported a drop. It is
  only a warning and clears by itself if data returns. To recover from a disconnect, click
  the chip's **x** and press **Connect device** again.
- **Battery percentage.** The hub only reports its battery level when it chooses to, and
  the page can only show what it is sent. Hover over a chip's battery to see when the last
  report arrived and how many reports there have been. The browser console (Cmd+Opt+J)
  logs a `battery reading` line for every report. A battery number on a red chip may be
  out of date.
- **It connects only some of the time.** The page retries automatically
  (up to five attempts). Open the browser console (Cmd+Opt+J) to see
  `BLE connect attempt N/5 failed` lines.
- **A hub appears in the chooser with no name.** Chrome sometimes does not
  report the name. The page works out the device type from the data the hub
  sends, and falls back to asking you which type it is.
- **Nothing happens on load.** Hard-reload (Cmd+Shift+R). The page needs the
  internet to fetch PyScript and Plotly.
- **Hub won't connect at all.** Switch it off and on, and remove any stale
  entry for it in your computer's Bluetooth settings.

## For editing

Everything is plain files; there is no build step. To run a copy locally:

```
cd "Public stuff/AnnaCode"
python3 serve.py
```

then open `http://localhost:8000/` (builder) or
`http://localhost:8000/trainer.html` (trainer) in Chrome. `localhost` is
allowed to use Bluetooth. `python3 serve.py 8001` picks another port.

`serve.py` is `python3 -m http.server` with browser caching switched off. Prefer it when
you edit files or switch branches: the plain server lets Chrome keep old copies, and
PyScript fetches its `.py` files itself, so the page can keep running stale code (for
example a new button that does nothing) even after a hard reload.

```
index.html, styles.css, main.py   Builder page and its entry point
Device.py                         Hub connection, device state, output routing
glue/ network/ misc_ui/ plot.py   Builder UI, network model, plotting
JS/ble.js                         Web Bluetooth wrapper (connect with retries)
pyscript.toml                     Builder config: packages and file map
trainer.html, trainer.toml        Trainer page and its config
trainer/                          Trainer sources (same layout, own copies)
```

Notes:

- **Flat Python imports.** PyScript copies each source file into one flat
  folder (`./glue/state.py` becomes `state.py`), so modules import each other
  as `import state`, not `from glue import state`. The mapping lives in the
  `[files]` table of `pyscript.toml` / `trainer.toml`. Add a new file there
  or it won't be found.
- **The two pages have separate copies of `Device.py`.** A fix to Bluetooth
  handling must be made in both `Device.py` and `trainer/Device.py`
  (`JS/ble.js` and `trainer/JS/ble.js` likewise).
- **`legoeducation` is pinned to 1.0.6** in both `.toml` files. Version 1.1.1
  replaced the worker the page patches for the browser, and breaks it.
- The builder page still includes the original PyScript analytics snippet;
  the trainer page does not.

## Where it came from

Adapted from the Tufts CEEO apps
[network-builder](https://tuftsceeo.pyscriptapps.com/network-builder/latest/)
and [network-trainer](https://tuftsceeo.pyscriptapps.com/network-trainer/latest/)
(source: [tuftsceeo/NeuralNetworkEducation](https://github.com/tuftsceeo/NeuralNetworkEducation)).
Changes here: more reliable Bluetooth pairing, hub type detection when Chrome
gives no name, card-color labels, an already-connected alert, live values next
to each device dropdown, and a trainer page without the lesson plans.
