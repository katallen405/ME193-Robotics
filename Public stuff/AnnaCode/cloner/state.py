"""Shared state for the Table Cloner page.

Device.py and power.py (shared with the Trainer) read a few names from here, so this stands in
for the Trainer's much bigger state.py. Other modules use `state.x`, never
`from state import x`, so changes are visible everywhere.
"""
from pyscript import document

devices: list = []

# trainer/misc_ui/power.py (Save power) is shared with the Trainer and reads these names.
# The Cloner's three sensor dropdowns play the part of the Trainer's Input nodes
# (their element ids are dev-input-left / -front / -right), and Record / Run play the part of
# Collect / Run.
inputs: list = [{"id": "left"}, {"id": "front"}, {"id": "right"}]
outputs: list = []
is_running = False           # Run table is on
is_generating_data = False   # Record is on


def get_id(id_: str):
    return document.getElementById(id_)
