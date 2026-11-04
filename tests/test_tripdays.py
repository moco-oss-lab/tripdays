import unittest
from datetime import date

from tripdays import Leg, assess_trip, parse_leg


def leg(place, arrive, depart):
    return Leg(place, date.fromisoformat(arrive), date.fromisoformat(depart))


class TestTripdays(unittest.TestCase):
    def test_nights_and_totals(self):
        report = assess_trip([
            leg("Lima", "2027-01-01", "2027-01-04"),
            leg("Cusco", "2027-01-04", "2027-01-08"),
        ])
        self.assertEqual([s.nights for s in report.stays], [3, 4])
        self.assertEqual(report.total_nights, 7)
        self.assertEqual(report.total_days, 7)

    def test_gap_is_reported_not_a_warning(self):
        report = assess_trip([
            leg("Lima", "2027-01-01", "2027-01-03"),
            leg("Cusco", "2027-01-05", "2027-01-07"),
        ])
        self.assertEqual(len(report.gaps), 1)
        self.assertEqual(report.gaps[0].days, 2)
        self.assertEqual(report.warnings, [])

    def test_overlap_is_a_warning(self):
        report = assess_trip([
            leg("Lima", "2027-01-01", "2027-01-05"),
            leg("Cusco", "2027-01-04", "2027-01-07"),
        ])
        self.assertTrue(any("overlap" in w for w in report.warnings))

    def test_same_day_move_is_a_warning(self):
        report = assess_trip([
            leg("Lima", "2027-01-01", "2027-01-04"),
            leg("Cusco", "2027-01-04", "2027-01-06"),
        ])
        self.assertTrue(any("same-day move" in w for w in report.warnings))

    def test_unsorted_input_is_sorted(self):
        report = assess_trip([
            leg("Cusco", "2027-01-04", "2027-01-06"),
            leg("Lima", "2027-01-01", "2027-01-04"),
        ])
        self.assertEqual([s.leg.place for s in report.stays], ["Lima", "Cusco"])

    def test_day_visit_flagged(self):
        report = assess_trip([leg("Lima", "2027-01-01", "2027-01-01")])
        self.assertTrue(any("day visit" in w for w in report.warnings))

    def test_invalid_leg_rejected(self):
        with self.assertRaises(ValueError):
            parse_leg({"place": "Lima", "arrive": "2027-01-05",
                       "depart": "2027-01-01"})
        with self.assertRaises(ValueError):
            assess_trip([])


if __name__ == "__main__":
    unittest.main()
