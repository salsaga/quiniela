"""Tests de las reglas de puntuación (ver templates/reglas.html)."""

from django.test import SimpleTestCase

from pool.services.scoring import calculate_points


class CalculatePointsTests(SimpleTestCase):
    def test_exact_score_with_winner(self):
        self.assertEqual(calculate_points(2, 1, 2, 1), 5)
        self.assertEqual(calculate_points(0, 3, 0, 3), 5)

    def test_exact_score_draw(self):
        self.assertEqual(calculate_points(1, 1, 1, 1), 4)
        self.assertEqual(calculate_points(0, 0, 0, 0), 4)

    def test_winner_and_goal_difference(self):
        self.assertEqual(calculate_points(3, 2, 2, 1), 4)
        self.assertEqual(calculate_points(0, 2, 1, 3), 4)

    def test_winner_only(self):
        self.assertEqual(calculate_points(1, 0, 3, 1), 3)
        self.assertEqual(calculate_points(0, 1, 1, 4), 3)

    def test_draw_not_exact(self):
        self.assertEqual(calculate_points(1, 1, 2, 2), 3)
        self.assertEqual(calculate_points(3, 3, 0, 0), 3)

    def test_wrong_outcome(self):
        self.assertEqual(calculate_points(2, 0, 0, 2), 0)
        self.assertEqual(calculate_points(1, 0, 0, 1), 0)
        self.assertEqual(calculate_points(1, 1, 2, 1), 0)
        self.assertEqual(calculate_points(2, 1, 1, 1), 0)

    def test_missing_data_returns_none(self):
        self.assertIsNone(calculate_points(None, 1, 2, 1))
        self.assertIsNone(calculate_points(1, None, 2, 1))
        self.assertIsNone(calculate_points(1, 1, None, 1))
        self.assertIsNone(calculate_points(1, 1, 2, None))
