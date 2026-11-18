"""Run from the AnnaCode folder:  python3 -m unittest discover tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "network"))
import mode_logic as ml  # noqa: E402


class RequestedMode(unittest.TestCase):
    def test_the_redirect_targets(self):
        self.assertEqual(ml.requested_mode("?mode=training", "beginner"), "training")
        self.assertEqual(ml.requested_mode("?mode=cloner", "beginner"), "cloner")

    def test_every_tab_can_be_asked_for(self):
        for mode in ml.MODES:
            self.assertEqual(ml.requested_mode(f"?mode={mode}", "x"), mode)
            self.assertEqual(ml.requested_mode(f"#{mode}", "x"), mode)

    def test_query_and_hash_are_both_searched(self):
        self.assertEqual(ml.requested_mode("?a=1#cloner", "beginner"), "cloner")
        self.assertEqual(ml.requested_mode("?other=1&mode=fitting", "beginner"), "fitting")

    def test_no_request_keeps_the_default(self):
        self.assertEqual(ml.requested_mode("", "advanced"), "advanced")
        self.assertEqual(ml.requested_mode("?mode=nonsense", "beginner"), "beginner")
        self.assertEqual(ml.requested_mode(None, "beginner"), "beginner")

    def test_cloner_is_a_known_tab(self):
        self.assertIn("cloner", ml.MODES)


if __name__ == "__main__":
    unittest.main()
