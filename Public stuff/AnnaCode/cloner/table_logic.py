"""Pure logic for the Table Cloner: behavior cloning with a lookup table.

No PyScript or DOM in here, so it can be unit-tested with plain Python
(see AnnaCode/tests/test_table_logic.py). main.py is the glue.

The robot has three color sensors facing left, front and right. Each one is
turned into "object here / not here", so the world is one of 8 patterns. While a
human drives with the joystick, every (pattern, what the human did) pair is
counted in a table. To drive itself the robot looks up its current pattern and
does the action with the highest count.
"""

# What the human can teach. Each is a (left wheel, right wheel) pair, forward positive.
ACTIONS = ("Forward", "Left", "Right", "Back", "Stop")
_WHEELS = {
    "Forward": (1, 1),
    "Back": (-1, -1),
    "Left": (-1, 1),    # spin left: right wheel forward, left wheel back
    "Right": (1, -1),
    "Stop": (0, 0),
}

SENSORS = ("Left", "Front", "Right")
N_PATTERNS = 8

DEFAULT_THRESHOLD = 40.0
DEFAULT_SPEED = 40
STICK_DEADBAND = 15.0   # stick percent below which the human is "not driving"


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def detect(reading, threshold: float = DEFAULT_THRESHOLD, object_is_bright: bool = True) -> bool:
    """True when a sensor sees an object. A reflection reading is None until the first
    notification, which counts as 'nothing there'. A close object usually reads brighter;
    flip object_is_bright for a dark object on a light floor."""
    v = _num(reading)
    if v is None:
        return False
    return v >= threshold if object_is_bright else v <= threshold


def pattern_index(left: bool, front: bool, right: bool) -> int:
    """0..7, bit 2 = left, bit 1 = front, bit 0 = right."""
    return (4 if left else 0) + (2 if front else 0) + (1 if right else 0)


def pattern_bits(index: int) -> tuple[bool, bool, bool]:
    return bool(index & 4), bool(index & 2), bool(index & 1)


def pattern_name(index: int) -> str:
    l, f, r = pattern_bits(index)
    names = [n for n, on in zip(SENSORS, (l, f, r)) if on]
    return " + ".join(names) if names else "Clear"


def classify_action(left_stick, right_stick, deadband: float = STICK_DEADBAND):
    """Turn the two tank-drive sticks (percent, forward positive) into one of the
    actions, or None when the human isn't pushing anything (nothing to learn)."""
    sl, sr = _num(left_stick) or 0.0, _num(right_stick) or 0.0
    if abs(sl) <= deadband:
        sl = 0.0
    if abs(sr) <= deadband:
        sr = 0.0
    if sl == 0.0 and sr == 0.0:
        return None
    forward = (sl + sr) / 2.0
    turn = (sr - sl) / 2.0   # positive: right wheel faster, so the car turns left
    if abs(turn) >= abs(forward):
        return "Left" if turn > 0 else "Right"
    return "Forward" if forward > 0 else "Back"


def motor_commands(action: str, speed: float = DEFAULT_SPEED, reverse: bool = False) -> tuple[int, int]:
    """(LeftSpeed, RightSpeed) to send to a Double Motor. The right motor is mirrored,
    the same convention as teleop_logic.command_for."""
    lw, rw = _WHEELS.get(action, (0, 0))
    s = max(0.0, min(100.0, _num(speed) or 0.0))
    left, right = lw * s, -rw * s
    if reverse:
        left, right = -left, -right
    return int(round(left)) + 0, int(round(right)) + 0   # + 0 turns -0 into 0


class BehaviorTable:
    """counts[pattern][action] = how many times the human chose that action there."""

    def __init__(self):
        self.counts = [{a: 0 for a in ACTIONS} for _ in range(N_PATTERNS)]

    def add(self, pattern: int, action: str, n: int = 1):
        if action in ACTIONS and 0 <= pattern < N_PATTERNS:
            self.counts[pattern][action] += n

    def total(self, pattern: int | None = None) -> int:
        if pattern is None:
            return sum(self.total(p) for p in range(N_PATTERNS))
        return sum(self.counts[pattern].values())

    def clear(self):
        self.__init__()

    def best(self, pattern: int):
        """The most-counted action for one pattern, or None if it has no examples.
        Ties go to the action listed first in ACTIONS."""
        row = self.counts[pattern]
        top = max(row.values())
        if top == 0:
            return None
        return next(a for a in ACTIONS if row[a] == top)

    def predict(self, pattern: int):
        """(action, source). source is 'exact' when this pattern has examples, 'nearest'
        when it borrows from the most similar pattern that does (fewest sensors different,
        then most examples), and 'none' (action 'Stop') when the table is empty."""
        action = self.best(pattern)
        if action is not None:
            return action, "exact"
        candidates = [p for p in range(N_PATTERNS) if self.total(p) > 0]
        if not candidates:
            return "Stop", "none"
        nearest = min(candidates, key=lambda p: (bin(p ^ pattern).count("1"), -self.total(p), p))
        return self.best(nearest), "nearest"

    def confidence(self, pattern: int) -> float:
        """Share of this pattern's examples that agree with its best action (0 if none)."""
        total = self.total(pattern)
        if total == 0:
            return 0.0
        return max(self.counts[pattern].values()) / total

    def to_dict(self) -> dict:
        return {"counts": self.counts}

    @classmethod
    def from_dict(cls, data) -> "BehaviorTable":
        table = cls()
        try:
            for p, row in enumerate(data["counts"][:N_PATTERNS]):
                for a in ACTIONS:
                    table.counts[p][a] = max(0, int(row.get(a, 0)))
        except (TypeError, KeyError, ValueError, AttributeError):
            return cls()
        return table
