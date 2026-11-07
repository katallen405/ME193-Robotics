"""Run from the AnnaCode folder:  python3 -m unittest discover tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "trainer", "network"))
import fit_logic as fl  # noqa: E402


class XRange(unittest.TestCase):
    def test_no_examples_uses_the_default(self):
        self.assertEqual(fl.x_range([]), fl.DEFAULT_RANGE)

    def test_pads_the_span_of_the_examples(self):
        lo, hi = fl.x_range([20, 80])
        self.assertAlmostEqual(lo, 14.0)
        self.assertAlmostEqual(hi, 86.0)

    def test_order_of_examples_does_not_matter(self):
        self.assertEqual(fl.x_range([80, 20, 50]), fl.x_range([20, 50, 80]))

    def test_always_contains_every_example(self):
        xs = [-37.5, 12, 90, 3]
        lo, hi = fl.x_range(xs)
        self.assertLess(lo, min(xs))
        self.assertGreater(hi, max(xs))

    def test_single_distinct_value_gets_a_window(self):
        lo, hi = fl.x_range([80, 80, 80])
        self.assertLess(lo, 80)
        self.assertGreater(hi, 80)

    def test_single_value_at_zero_still_gets_a_window(self):
        lo, hi = fl.x_range([0])
        self.assertEqual((lo, hi), (-1.0, 1.0))

    def test_negative_ranges(self):
        lo, hi = fl.x_range([-100, -20])
        self.assertAlmostEqual(lo, -108.0)
        self.assertAlmostEqual(hi, -12.0)


class Grid(unittest.TestCase):
    def test_includes_both_ends(self):
        g = fl.grid(0, 10, 11)
        self.assertEqual(g[0], 0)
        self.assertAlmostEqual(g[-1], 10)
        self.assertEqual(len(g), 11)

    def test_evenly_spaced(self):
        g = fl.grid(-100, 100, 5)
        self.assertEqual(g, [-100.0, -50.0, 0.0, 50.0, 100.0])

    def test_too_few_points(self):
        self.assertEqual(fl.grid(3, 9, 1), [3.0])

    def test_default_size(self):
        self.assertEqual(len(fl.grid(0, 1)), 60)


class Means(unittest.TestCase):
    def test_column_means(self):
        self.assertEqual(fl.means([[1, 10], [3, 30]]), [2.0, 20.0])

    def test_no_rows(self):
        self.assertEqual(fl.means([]), [])

    def test_single_column(self):
        self.assertEqual(fl.means([[2], [4], [6]]), [4.0])


if __name__ == "__main__":
    unittest.main()
