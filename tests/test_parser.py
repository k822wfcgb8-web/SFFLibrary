"""Tests for build.py. Run with:  python3 -m unittest discover tests"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build  # noqa: E402

with open(os.path.join(HERE, "sample_master.md"), encoding="utf-8") as f:
    SAMPLE = f.read()


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.summary, self.problems = build.parse(SAMPLE)

    def find(self, year, month):
        return [r for r in self.rows if r["year"] == year and r["month"] == month]

    def test_no_problems_and_valid(self):
        self.assertEqual(self.problems, [])
        self.assertEqual(build.validate(self.rows, self.summary), [])

    def test_counts(self):
        count = lambda s: sum(r["status"] == s for r in self.rows)
        self.assertEqual(count("read"), 19)
        self.assertEqual(count("undated"), 2)
        self.assertEqual(count("no-meeting"), 2)
        self.assertEqual(count("unknown"), 2)
        self.assertEqual(count("planning"), 1)
        self.assertEqual(count("upcoming"), 1)

    def test_two_books_in_one_month(self):
        titles = [r["title"] for r in self.find(2004, 10)]
        self.assertEqual(titles, ["Bimbos of the Death Sun", "Zombies of the Gene Pool"])

    def test_parts(self):
        apr, may = self.find(2005, 4)[0], self.find(2005, 5)[0]
        self.assertEqual(apr["title"], "Cryptonomicon")
        self.assertEqual(apr["part"], "part 1 of 2")
        self.assertEqual(may["part"], "part 2 of 2")

    def test_status_rows(self):
        self.assertEqual(self.find(2004, 2)[0]["status"], "unknown")
        self.assertEqual(self.find(2004, 7)[0]["status"], "no-meeting")
        self.assertEqual(self.find(2004, 12)[0]["status"], "planning")
        self.assertEqual(self.find(2005, 12)[0]["status"], "upcoming")

    def test_special_and_author_forms(self):
        self.assertEqual(self.find(2005, 1)[0]["title"], "Multiple Titles")
        self.assertEqual(self.find(2004, 5)[0]["author"], "Modesitt Jr., L. E.")
        self.assertEqual(self.find(2004, 11)[0]["author"], "Niven, Larry and Pournelle, Jerry")
        self.assertEqual(self.find(2005, 2)[0]["author"], "Miéville, China")

    def test_previously_read(self):
        self.assertEqual(self.find(2005, 3)[0]["previouslyRead"], ["2004-01"])
        self.assertEqual(self.find(2005, 6)[0]["previouslyRead"], ["2004-01", "2005-03"])

    def test_undated(self):
        und = [r for r in self.rows if r["status"] == "undated"]
        self.assertEqual(und[1]["author"], "Friesner, Esther (editor)")
        self.assertEqual(und[1]["previouslyRead"], ["2004-06"])
        self.assertIsNone(und[0]["year"])


class ValidationTests(unittest.TestCase):
    def test_missing_month_is_reported(self):
        broken = SAMPLE.replace("| Sep | Pawn of Prophecy | Eddings, David | The Belgariad #1 |  |\n", "")
        rows, summary, _ = build.parse(broken)
        problems = build.validate(rows, summary)
        self.assertTrue(any("2004 has no row for: Sep" in p for p in problems), problems)

    def test_count_mismatch_is_reported(self):
        rows, summary, _ = build.parse(SAMPLE.replace("Book rows (dated): 19", "Book rows (dated): 20"))
        problems = build.validate(rows, summary)
        self.assertTrue(any("Summary says 20 dated book rows" in p for p in problems), problems)

    def test_bad_row_reported_with_line_number(self):
        rows, summary, problems = build.parse(SAMPLE.replace("| Jun | Gateway |", "| June | Gateway |"))
        self.assertTrue(any(p.startswith("line ") and "June" in p for p in problems), problems)

    def test_unknown_status_reported(self):
        _, _, problems = build.parse(SAMPLE.replace("*Upcoming*", "*Cancelled*"))
        self.assertTrue(any("unknown status 'Cancelled'" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
