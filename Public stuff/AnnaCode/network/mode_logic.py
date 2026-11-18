"""Pure logic for the page's tabs (no PyScript or DOM here, so it is unit-tested with plain Python;
see tests/test_mode_logic.py). main.py is the glue."""

# The tab ids, in the order the tabs appear. "beginner" is the Basic tab.
MODES = ("beginner", "advanced", "fitting", "training", "cloner")


def requested_mode(location_text: str, default: str) -> str:
    """The tab the page address asks for, or `default`. `location_text` is the address's query
    string plus its hash, for example "?mode=training" or "#cloner". trainer.html and cloner.html
    redirect to index.html?mode=training and index.html?mode=cloner."""
    text = location_text or ""
    for mode in MODES:
        if f"mode={mode}" in text or f"#{mode}" in text:
            return mode
    return default
