#!/usr/bin/env python

from collections.abc import Iterator
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

DATE_PARTS_COUNT = 3
MIN_MONTH = 1
MAX_MONTH = 12
FEBRUARY = 2
SHORT_MONTHS = (4, 6, 9, 11)
MAX_DAY = 31
LEAP_DIVISOR = 4
CENTURY_DIVISOR = 100
DIVISOR_400 = 400

INCOME_ARGS_COUNT = 3
COST_CATEGORIES_ARGS_COUNT = 2
COST_ARGS_COUNT = 4
STATS_ARGS_COUNT = 2

AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"

ZERO_FLOAT = float(0)

StatsResult = tuple[float, float, float, dict[str, float]]

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    base_rule = year % LEAP_DIVISOR == 0 and year % CENTURY_DIVISOR != 0
    exception_rule = year % DIVISOR_400 == 0
    return base_rule or exception_rule


def parse_date_parts(parts: list[str]) -> tuple[int, int, int]:
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    return day, month, year


def max_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        return 29 if is_leap_year(year) else 28
    if month in SHORT_MONTHS:
        return 30
    return MAX_DAY


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None
    try:
        day, month, year = parse_date_parts(parts)
    except ValueError:
        return None
    if not (MIN_MONTH <= month <= MAX_MONTH):
        return None
    max_day = max_days_in_month(month, year)
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
    financial_transactions_storage.append({AMOUNT_KEY: amount, DATE_KEY: date_tuple})
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
    financial_transactions_storage.append({CATEGORY_KEY: category_name, AMOUNT_KEY: amount, DATE_KEY: date_tuple})
    return OP_SUCCESS_MSG


def generate_category_strings() -> Iterator[str]:
    for key, values in EXPENSE_CATEGORIES.items():
        for value in values:
            yield f"{key}::{value}"


def cost_categories_handler() -> str:
    entries: list[str] = []
    entries.extend(generate_category_strings())
    return "\n".join(entries)


def is_expense_record(record: dict[str, Any]) -> bool:
    return CATEGORY_KEY in record


def is_same_month_and_day_before(
    tr_date: tuple[int, int, int],
    year: int,
    month: int,
    day: int,
) -> bool:
    tr_day, tr_month, tr_year = tr_date
    return tr_year == year and tr_month == month and tr_day <= day


def process_single_transaction(
    record: dict[str, Any],
    report_tuple: tuple[int, int, int],
    details: dict[str, float],
) -> tuple[float, float, float]:
    tr_date = record.get(DATE_KEY)
    if tr_date is None:
        return ZERO_FLOAT, ZERO_FLOAT, ZERO_FLOAT
    year, month, day = report_tuple
    total_delta = ZERO_FLOAT
    month_income_delta = ZERO_FLOAT
    month_expense_delta = ZERO_FLOAT
    is_exp = is_expense_record(record)
    amount = record[AMOUNT_KEY]
    if tr_date <= report_tuple:
        total_delta = -amount if is_exp else amount
    if is_same_month_and_day_before(tr_date, year, month, day):
        if is_exp:
            month_expense_delta = amount
            target = record[CATEGORY_KEY].split("::")[-1]
            details[target] = details.get(target, ZERO_FLOAT) + amount
        else:
            month_income_delta = amount
    return total_delta, month_income_delta, month_expense_delta


def compute_stats(day: int, month: int, year: int) -> StatsResult:
    total_capital = ZERO_FLOAT
    month_income = ZERO_FLOAT
    month_expenses = ZERO_FLOAT
    details: dict[str, float] = {}
    report_tuple = (year, month, day)

    for tr in financial_transactions_storage:
        delta_cap, delta_inc, delta_exp = process_single_transaction(tr, report_tuple, details)
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
    if len(parts) != INCOME_ARGS_COUNT:
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
    if len(parts) == COST_CATEGORIES_ARGS_COUNT and parts[1] == "categories":
        print(cost_categories_handler())
        return
    if len(parts) != COST_ARGS_COUNT:
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
    if len(parts) != STATS_ARGS_COUNT:
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
