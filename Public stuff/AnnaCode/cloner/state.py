"""Shared state for the Table Cloner page.

Device.py (shared with the Trainer) only needs `state.devices`, so this stands in
for the Trainer's much bigger state.py. Other modules use `state.x`, never
`from state import x`, so changes are visible everywhere.
"""
from pyscript import document

devices: list = []


def get_id(id_: str):
    return document.getElementById(id_)
