"""Pure logic for the Fit plot's line (no PyScript or DOM here, so it is unit-tested with
plain Python; see AnnaCode/tests/test_fit_logic.py).

The fit line is the network's own answer swept across the first input: for a grid of x
values, run the network and plot each output. The plot's dots are your examples, so a
well-trained network's line runs through them.
"""

DEFAULT_RANGE = (-100.0, 100.0)   # when there are no examples yet (sticks span this; sensors sit inside it)


def x_range(xs, pad_fraction: float = 0.1, default=DEFAULT_RANGE):
    """(low, high) to draw the line over: the examples' span plus a little padding.
    No examples: the default. One distinct value: a window around it."""
    xs = [float(x) for x in xs]
    if not xs:
        return default
    lo, hi = min(xs), max(xs)
    if hi == lo:
        pad = max(1.0, abs(lo) * 0.5)
        return lo - pad, hi + pad
    pad = (hi - lo) * pad_fraction
    return lo - pad, hi + pad


def grid(lo: float, hi: float, n: int = 60):
    """n evenly spaced values from lo to hi, both included."""
    if n < 2:
        return [float(lo)]
    step = (hi - lo) / (n - 1)
    return [lo + step * i for i in range(n)]


def means(rows):
    """Column means of a list of equal-length rows; [] for no rows."""
    rows = [list(r) for r in rows]
    if not rows:
        return []
    return [sum(col) / len(rows) for col in zip(*rows)]
