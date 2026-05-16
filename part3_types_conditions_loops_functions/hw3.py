#!/usr/bin/env python

from typing import Any, Iterator

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

_ZERO_FLOAT = float(0)

StatsResult = tuple[float, float, float, dict[str, float]]

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    base_rule = year % _LEAP_DIVISOR == 0 and year % _CENTURY_DIVISOR != 0
    exception_rule = year % _400_DIVISOR == 0
    return base_rule or exception_rule


def _parse_date_parts(parts: list[str]) -> tuple[int, int, int]:
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    return day, month, year


def _max_days_in_month(month: int, year: int) -> int:
    if month == _FEBRUARY:
        return 29 if is_leap_year(year) else 28
    if month in _SHORT_MONTHS:
        return 30
    return _MAX_DAY


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != _DATE_PARTS_COUNT:
        return None
    try:
        day, month, year = _parse_date_parts(parts)
    except ValueError:
        return None
    if not (_MIN_MONTH <= month <= _MAX_MONTH):
        return None
    max_day = _max_days_in_month(month, year)
    if not (1 <= day <= max_day):
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
    financial_transactions_storage.append({_AMOUNT_KEY: amount, _DATE_KEY: date_tuple})
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
    financial_transactions_storage.append({_CATEGORY_KEY: category_name, _AMOUNT_KEY: amount, _DATE_KEY: date_tuple})
    return OP_SUCCESS_MSG


def _generate_category_strings() -> Iterator[str]:
    for key, values in EXPENSE_CATEGORIES.items():
        for value in values:
            yield f"{key}::{value}"


def cost_categories_handler() -> str:
    entries: list[str] = []
    entries.extend(_generate_category_strings())
    return "\n".join(entries)


def _is_expense(record: dict[str, Any]) -> bool:
    return _CATEGORY_KEY in record


def _is_same_month_and_day_before(
    tr_date: tuple[int, int, int],
    year: int,
    month: int,
    day: int,
) -> bool:
    tr_day, tr_month, tr_year = tr_date
    return tr_year == year and tr_month == month and tr_day <= day


def _process_transaction(
    record: dict[str, Any],
    report_tuple: tuple[int, int, int],
    details: dict[str, float],
) -> tuple[float, float, float]:
    tr_date = record.get(_DATE_KEY)
    if tr_date is None:
        return _ZERO_FLOAT, _ZERO_FLOAT, _ZERO_FLOAT
    year, month, day = report_tuple
    total_delta = _ZERO_FLOAT
    month_income_delta = _ZERO_FLOAT
    month_expense_delta = _ZERO_FLOAT
    is_exp = _is_expense(record)
    amount = record[_AMOUNT_KEY]
    if tr_date <= report_tuple:
        total_delta = -amount if is_exp else amount
    if _is_same_month_and_day_before(tr_date, year, month, day):
        if is_exp:
            month_expense_delta = amount
            target = record[_CATEGORY_KEY].split("::")[-1]
            details[target] = details.get(target, _ZERO_FLOAT) + amount
        else:
            month_income_delta = amount
    return total_delta, month_income_delta, month_expense_delta


def compute_stats(day: int, month: int, year: int) -> StatsResult:
    total_capital = _ZERO_FLOAT
    month_income = _ZERO_FLOAT
    month_expenses = _ZERO_FLOAT
    details: dict[str, float] = {}
    report_tuple = (year, month, day)

    for tr in financial_transactions_storage:
        delta_cap, delta_inc, delta_exp = _process_transaction(tr, report_tuple, details)
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


def process_single_input(line: str) -> None:
    parts = line.split()
    if not parts:
        return
    dispatch_command(parts)


def main() -> None:
    while True:
        line = read_user_line()
        if line is None:
            break
        if not line:
            continue
        process_single_input(line)


if __name__ == "__main__":
    main()
