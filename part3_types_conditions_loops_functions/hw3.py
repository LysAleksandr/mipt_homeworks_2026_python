#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

_DATE_PARTS_COUNT = 3
_MIN_MONTH = 1
_MAX_MONTH = 12
_FEBRUARY = 2
_SHORT_MONTHS = (4, 6, 9, 11)
_MAX_DAY = 31
_LEAP_DIVISOR = 4
_CENTURY_DIVISOR = 100
_400_DIVISOR = 400

_INCOME_ARGS_COUNT = 3
_COST_CATEGORIES_ARGS_COUNT = 2
_COST_ARGS_COUNT = 4
_STATS_ARGS_COUNT = 2

_AMOUNT_KEY = "amount"
_DATE_KEY = "date"
_CATEGORY_KEY = "category"

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    divisible_by_4 = year % _LEAP_DIVISOR == 0
    not_divisible_by_100 = year % _CENTURY_DIVISOR != 0
    divisible_by_400 = year % _400_DIVISOR == 0
    return (divisible_by_4 and not_divisible_by_100) or divisible_by_400


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != _DATE_PARTS_COUNT:
        return None
    try:
        day_str, month_str, year_str = parts[0], parts[1], parts[2]
        day = int(day_str)
        month = int(month_str)
        year = int(year_str)
    except ValueError:
        return None
    if month < _MIN_MONTH or month > _MAX_MONTH:
        return None
    if month == _FEBRUARY:
        max_day = 29 if is_leap_year(year) else 28
    elif month in _SHORT_MONTHS:
        max_day = 30
    else:
        max_day = _MAX_DAY
    if day < 1 or day > max_day:
        return None
    return (day, month, year)


def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append(
        {_AMOUNT_KEY: amount, _DATE_KEY: date_tuple}
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, expense_date: str) -> str:
    date_tuple = extract_date(expense_date)
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    if "::" not in category_name:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    common, target = category_name.split("::", 1)
    if common not in EXPENSE_CATEGORIES or target not in EXPENSE_CATEGORIES[common]:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    financial_transactions_storage.append(
        {_CATEGORY_KEY: category_name, _AMOUNT_KEY: amount, _DATE_KEY: date_tuple}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    entries = []
    for key, values in EXPENSE_CATEGORIES.items():
        for value in values:
            entries.append(f"{key}::{value}")
    return "\n".join(entries)


def _is_expense(record: dict[str, Any]) -> bool:
    return _CATEGORY_KEY in record


def _process_transaction(
    record: dict[str, Any],
    report_tuple: tuple[int, int, int],
    month: int,
    year: int,
    day: int,
    details: dict[str, float],
) -> tuple[float, float, float]:
    tr_date = record.get(_DATE_KEY)
    if tr_date is None:
        return 0, 0, 0
    total_delta = 0
    month_income_delta = 0
    month_expense_delta = 0
    is_exp = _is_expense(record)
    amount = record[_AMOUNT_KEY]
    if tr_date <= report_tuple:
        if is_exp:
            total_delta = -amount
        else:
            total_delta = amount
    if tr_date[1] == month and tr_date[2] == year and tr_date[0] <= day:
        if is_exp:
            month_expense_delta = amount
            target = record[_CATEGORY_KEY].split("::")[-1]
            details[target] = details.get(target, 0) + amount
        else:
            month_income_delta = amount
    return total_delta, month_income_delta, month_expense_delta


def compute_stats(
    day: int, month: int, year: int
) -> tuple[float, float, float, dict[str, float]]:
    total_capital = 0
    month_income = 0
    month_expenses = 0
    details: dict[str, float] = {}
    report_tuple = (year, month, day)

    for tr in financial_transactions_storage:
        delta_cap, delta_inc, delta_exp = _process_transaction(
            tr, report_tuple, month, year, day, details
        )
        total_capital += delta_cap
        month_income += delta_inc
        month_expenses += delta_exp
    return total_capital, month_income, month_expenses, details


def format_stats(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    details: dict[str, float],
) -> str:
    lines = []
    lines.append(f"Your statistics as of {report_date}:")
    lines.append(f"Total capital: {total_capital:.2f} rubles")
    profit = month_income - month_expenses
    if profit >= 0:
        lines.append(f"This month, the profit amounted to {profit:.2f} rubles.")
    else:
        loss = -profit
        lines.append(f"This month, the loss amounted to {loss:.2f} rubles.")
    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {month_expenses:.2f} rubles")
    lines.append("")
    lines.append("Details (category: amount):")
    if details:
        for i, cat in enumerate(sorted(details), 1):
            amt = details[cat]
            amt_str = str(int(amt)) if amt.is_integer() else f"{amt:.2f}"
            lines.append(f"{i}. {cat}: {amt_str}")
    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    parsed = extract_date(report_date)
    if parsed is None:
        return INCORRECT_DATE_MSG
    day, month, year = parsed
    capital, income, expense, det = compute_stats(day, month, year)
    return format_stats(report_date, capital, income, expense, det)


def handle_income(parts: list[str]) -> None:
    if len(parts) != _INCOME_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount_str = parts[1]
    date_str = parts[2]
    try:
        amount = float(amount_str.replace(",", "."))
    except ValueError:
        print(NONPOSITIVE_VALUE_MSG)
        return
    print(income_handler(amount, date_str))


def handle_cost(parts: list[str]) -> None:
    if len(parts) == _COST_CATEGORIES_ARGS_COUNT and parts[1] == "categories":
        print(cost_categories_handler())
        return
    if len(parts) != _COST_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    category_name = parts[1]
    amount_str = parts[2]
    date_str = parts[3]
    try:
        amount = float(amount_str.replace(",", "."))
    except ValueError:
        print(NONPOSITIVE_VALUE_MSG)
        return
    result = cost_handler(category_name, amount, date_str)
    print(result)
    if result == NOT_EXISTS_CATEGORY:
        print(cost_categories_handler())


def handle_stats(parts: list[str]) -> None:
    if len(parts) != _STATS_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    date_str = parts[1]
    if extract_date(date_str) is None:
        print(INCORRECT_DATE_MSG)
        return
    print(stats_handler(date_str))


def dispatch_command(parts: list[str]) -> None:
    command = parts[0]
    if command == "income":
        handle_income(parts)
    elif command == "cost":
        handle_cost(parts)
    elif command == "stats":
        handle_stats(parts)
    else:
        print(UNKNOWN_COMMAND_MSG)


def read_user_line() -> str | None:
    try:
        return input().strip()
    except EOFError:
        return None


def main() -> None:
    while True:
        line = read_user_line()
        if line is None:
            break
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        dispatch_command(parts)


if __name__ == "__main__":
    main()
