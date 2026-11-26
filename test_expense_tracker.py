import tempfile
import unittest
from pathlib import Path
from expense_tracker import Expense, add_expense, filter_expenses, search_expenses, totals_by_category, validate_amount, validate_date, format_summary

class ExpenseTrackerTests(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(validate_amount("25.50"), 25.50)
        with self.assertRaises(ValueError): validate_amount(0)
        self.assertEqual(validate_date("2026-01-10"), "2026-01-10")
        with self.assertRaises(ValueError): validate_date("10/01/2026")

    def test_csv_persistence_and_filtering(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "expenses.csv"
            add_expense(Expense("2026-11-20", "Food", 180, "Lunch"), path)
            add_expense(Expense("2026-11-21", "Travel", 50, "Bus"), path)
            from expense_tracker import load_expenses
            expenses = load_expenses(path)
            self.assertEqual(len(filter_expenses(expenses, month="2026-11", category="food")), 1)
            self.assertEqual(search_expenses(expenses, "lunch")[0].amount, 180)

    def test_totals_and_summary(self):
        expenses = [Expense("2026-11-01", "Food", 100, "A"), Expense("2026-11-02", "Food", 50, "B"), Expense("2026-11-03", "Travel", 25, "C")]
        self.assertEqual(totals_by_category(expenses), {"Food": 150, "Travel": 25})
        self.assertIn("TOTAL", format_summary(expenses, {("2026-11", "Food"): 200}, "2026-11"))

if __name__ == "__main__": unittest.main()
