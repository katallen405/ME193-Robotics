"""Run from the AnnaCode folder:  python3 -m unittest discover tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cloner"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "trainer", "network"))
import table_logic as tl  # noqa: E402
import teleop_logic as tele  # noqa: E402


class Detect(unittest.TestCase):
    def test_bright_object(self):
        self.assertTrue(tl.detect(80, 40))
        self.assertFalse(tl.detect(10, 40))

    def test_dark_object(self):
        self.assertTrue(tl.detect(10, 40, object_is_bright=False))
        self.assertFalse(tl.detect(80, 40, object_is_bright=False))

    def test_no_reading_is_clear(self):
        self.assertFalse(tl.detect(None))
        self.assertFalse(tl.detect(None, object_is_bright=False))


class Patterns(unittest.TestCase):
    def test_index_round_trip(self):
        for i in range(tl.N_PATTERNS):
            self.assertEqual(tl.pattern_index(*tl.pattern_bits(i)), i)

    def test_names(self):
        self.assertEqual(tl.pattern_name(0), "Clear")
        self.assertEqual(tl.pattern_name(tl.pattern_index(True, False, True)), "Left + Right")
        self.assertEqual(tl.pattern_name(7), "Left + Front + Right")


class Classify(unittest.TestCase):
    def test_idle(self):
        self.assertIsNone(tl.classify_action(0, 0))
        self.assertIsNone(tl.classify_action(10, -10))
        self.assertIsNone(tl.classify_action(None, None))

    def test_straight(self):
        self.assertEqual(tl.classify_action(80, 80), "Forward")
        self.assertEqual(tl.classify_action(-80, -80), "Back")

    def test_turns(self):
        self.assertEqual(tl.classify_action(-60, 60), "Left")
        self.assertEqual(tl.classify_action(60, -60), "Right")

    def test_one_stick_pivots(self):
        self.assertEqual(tl.classify_action(0, 100), "Left")
        self.assertEqual(tl.classify_action(100, 0), "Right")

    def test_gentle_curve_counts_as_forward(self):
        self.assertEqual(tl.classify_action(100, 70), "Forward")


class Motors(unittest.TestCase):
    def test_forward_mirrors_right_motor(self):
        self.assertEqual(tl.motor_commands("Forward", 40), (40, -40))

    def test_spin(self):
        self.assertEqual(tl.motor_commands("Left", 40), (-40, -40))
        self.assertEqual(tl.motor_commands("Right", 40), (40, 40))

    def test_stop_and_unknown(self):
        self.assertEqual(tl.motor_commands("Stop", 40), (0, 0))
        self.assertEqual(tl.motor_commands("nonsense", 40), (0, 0))

    def test_reverse_and_clamp(self):
        self.assertEqual(tl.motor_commands("Forward", 40, reverse=True), (-40, 40))
        self.assertEqual(tl.motor_commands("Forward", 500), (100, -100))

    def test_agrees_with_teleop_logic(self):
        self.assertEqual(tl.motor_commands("Forward", 50),
                         (tele.command_for("LeftSpeed", 100, 100, 50),
                          tele.command_for("RightSpeed", 100, 100, 50)))


class Table(unittest.TestCase):
    def test_empty_table_stops(self):
        self.assertEqual(tl.BehaviorTable().predict(3), ("Stop", "none"))

    def test_majority_wins(self):
        t = tl.BehaviorTable()
        t.add(2, "Left", 3)
        t.add(2, "Right", 1)
        self.assertEqual(t.predict(2), ("Left", "exact"))
        self.assertAlmostEqual(t.confidence(2), 0.75)

    def test_unseen_pattern_borrows_nearest(self):
        t = tl.BehaviorTable()
        t.add(tl.pattern_index(False, True, False), "Left", 5)   # object in front -> turn left
        # Front + Right was never taught; Front alone is one sensor away.
        self.assertEqual(t.predict(tl.pattern_index(False, True, True)), ("Left", "nearest"))

    def test_nearest_tie_prefers_more_examples(self):
        t = tl.BehaviorTable()
        t.add(1, "Right", 2)
        t.add(4, "Left", 9)
        self.assertEqual(t.predict(0), ("Left", "nearest"))

    def test_ignores_bad_input(self):
        t = tl.BehaviorTable()
        t.add(99, "Forward")
        t.add(0, "Teleport")
        self.assertEqual(t.total(), 0)

    def test_save_and_load(self):
        t = tl.BehaviorTable()
        t.add(5, "Back", 4)
        u = tl.BehaviorTable.from_dict(t.to_dict())
        self.assertEqual(u.counts, t.counts)

    def test_garbage_load_gives_empty(self):
        self.assertEqual(tl.BehaviorTable.from_dict({"nope": 1}).total(), 0)
        self.assertEqual(tl.BehaviorTable.from_dict(None).total(), 0)

    def test_clear(self):
        t = tl.BehaviorTable()
        t.add(1, "Forward")
        t.clear()
        self.assertEqual(t.total(), 0)


if __name__ == "__main__":
    unittest.main()
