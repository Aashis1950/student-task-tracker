"""Student Expense and Budget Tracker.

The application intentionally uses the standard library so it can run on
Amazon Linux or a lab computer without external packages.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

DATA_FILE = Path(__file__).with_name("expenses.csv")
BUDGET_FILE = Path(__file__).with_name("budgets.csv")

@dataclass(frozen=True)
class Expense:
    expense_date: str
    category: str
    amount: float
    description: str

    def as_row(self) -> list[str]:
        return [self.expense_date, self.category, f"{self.amount:.2f}", self.description]

def validate_date(value: str) -> str:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("date must use YYYY-MM-DD format") from exc
    if parsed > date.today():
        raise ValueError("expense date cannot be in the future")
    return value

def validate_amount(value: str | float) -> float:
    amount = float(value)
    if amount <= 0:
        raise ValueError("amount must be greater than zero")
    return round(amount, 2)

def add_expense(expense: Expense, path: Path = DATA_FILE) -> None:
    validate_date(expense.expense_date)
    validate_amount(expense.amount)
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as handle:
        writer = csv.writer(handle)
        if needs_header:
            writer.writerow(["date", "category", "amount", "description"])
        writer.writerow(expense.as_row())

def load_expenses(path: Path = DATA_FILE) -> list[Expense]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return [Expense(r["date"], r["category"], float(r["amount"]), r["description"]) for r in csv.DictReader(handle)]

def filter_expenses(expenses: Iterable[Expense], month: str | None = None, category: str | None = None) -> list[Expense]:
    result = list(expenses)
    if month:
        result = [e for e in result if e.expense_date.startswith(month)]
    if category:
        result = [e for e in result if e.category.casefold() == category.casefold()]
    return result

def search_expenses(expenses: Iterable[Expense], text: str) -> list[Expense]:
    needle = text.casefold()
    return [e for e in expenses if needle in f"{e.category} {e.description}".casefold()]

def totals_by_category(expenses: Iterable[Expense]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for expense in expenses:
        totals[expense.category] = round(totals.get(expense.category, 0) + expense.amount, 2)
    return dict(sorted(totals.items()))

def load_budgets(path: Path = BUDGET_FILE) -> dict[tuple[str, str], float]:
    if not path.exists():
        return {}
    with path.open(newline="") as handle:
        return {(r["month"], r["category"]): float(r["limit"]) for r in csv.DictReader(handle)}

def save_budget(month: str, category: str, limit: float, path: Path = BUDGET_FILE) -> None:
    validate_amount(limit)
    budgets = load_budgets(path)
    budgets[(month, category)] = round(float(limit), 2)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle); writer.writerow(["month", "category", "limit"])
        for (m, c), amount in sorted(budgets.items()): writer.writerow([m, c, f"{amount:.2f}"])

def format_summary(expenses: Iterable[Expense], budgets: dict[tuple[str, str], float] | None = None, month: str = "") -> str:
    selected = list(expenses); totals = totals_by_category(selected)
    lines = [f"STUDENT EXPENSE & BUDGET REPORT — {month}", "=" * 40]
    for category, amount in totals.items():
        limit = (budgets or {}).get((month, category))
        suffix = f" / budget {limit:.2f}" if limit is not None else ""
        lines.append(f"{category:<14} {amount:>9.2f}{suffix}")
    lines.append("-" * 34)
    lines.append(f"TOTAL          {sum(totals.values()):>9.2f}")
    return "\n".join(lines)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track expenses and category budgets")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add"); add.add_argument("--date", required=True); add.add_argument("--category", required=True); add.add_argument("--amount", required=True, type=float); add.add_argument("--description", required=True)
    listing = sub.add_parser("list"); listing.add_argument("--month"); listing.add_argument("--category")
    report = sub.add_parser("report"); report.add_argument("--month", required=True)
    search = sub.add_parser("search"); search.add_argument("--text", required=True)
    budget = sub.add_parser("budget"); budget_sub = budget.add_subparsers(dest="budget_command", required=True)
    bset = budget_sub.add_parser("set"); bset.add_argument("--month", required=True); bset.add_argument("--category", required=True); bset.add_argument("--limit", required=True, type=float)
    status = budget_sub.add_parser("status"); status.add_argument("--month", required=True)
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv); expenses = load_expenses()
    if args.command == "add":
        add_expense(Expense(args.date, args.category, args.amount, args.description)); print("Expense added successfully.")
    elif args.command == "list":
        for e in filter_expenses(expenses, args.month, args.category): print(f"{e.expense_date} | {e.category:<12} | {e.amount:>8.2f} | {e.description}")
    elif args.command == "search":
        for e in search_expenses(expenses, args.text): print(f"{e.expense_date} | {e.category} | {e.amount:.2f} | {e.description}")
    elif args.command == "report": print(format_summary(filter_expenses(expenses, month=args.month), load_budgets(), args.month))
    elif args.command == "budget" and args.budget_command == "set": save_budget(args.month, args.category, args.limit); print("Budget saved successfully.")
    elif args.command == "budget" and args.budget_command == "status": print(format_summary(filter_expenses(expenses, month=args.month), load_budgets(), args.month))
    return 0

if __name__ == "__main__": raise SystemExit(main())
