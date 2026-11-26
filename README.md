# Student Expense and Budget Tracker

A medium-level Python command-line application for recording student expenses, setting category budgets, searching transactions, and generating monthly summaries.

## Features

- Add validated expenses with date, category, amount, and description
- Store transactions in a CSV file
- List and search expenses by month or category
- Set monthly category budgets
- Generate monthly totals and budget alerts
- Unit tests for validation, filtering, totals, and budget status

## Usage

```bash
python3 expense_tracker.py add --date 2026-11-20 --category Food --amount 180 --description "Lunch"
python3 expense_tracker.py list --month 2026-11
python3 expense_tracker.py report --month 2026-11
python3 expense_tracker.py budget set --month 2026-11 --category Food --limit 5000
python3 expense_tracker.py budget status --month 2026-11
python3 expense_tracker.py search --text lunch
```
