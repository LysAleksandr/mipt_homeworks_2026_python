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
_30_DAY_MONTHS = (4, 6, 9, 11)
_MAX_DAY = 31
_MAX_DAY_30 = 30
_LEAP_DIVISOR = 4
_CENTURY_DIVISOR = 100
_400_DIVISOR = 400

_INCOME_ARGS_COUNT = 3
_COST_CATEGORIES_ARGS_COUNT = 2
_COST_ARGS_COUNT = 4
_STATS_ARGS_COUNT = 2

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return (year % _LEAP_DIVISOR == 0 and year % _CENTURY_DIVISOR != 0) or (
        year % _400_DIVISOR == 0
    )


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != _DATE_PARTS_COUNT:
        return None
    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None
    if month < _MIN_MONTH or month > _MAX_MONTH:
        return None
    if month == _FEBRUARY:
        max_day = 29 if is_leap_year(year) else 28
    elif month in _30_DAY_MONTHS:
        max_day = _MAX_DAY_30
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
    financial_transactions_storage.append({"amount": amount, "date": date_tuple})
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
        {"category": category_name, "amount": amount, "date": date_tuple}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{k}::{v}" for k, kv in EXPENSE_CATEGORIES.items() for v in kv
    )


def compute_stats(
    day: int, month: int, year: int
) -> tuple[float, float, float, dict[str, float]]:
    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    details: dict[str, float] = {}
    report_tuple = (year, month, day)

    for tr in financial_transactions_storage:
        tr_date = tr.get("date")
        if tr_date is None:
            continue
        is_expense = "category" in tr
        if tr_date <= report_tuple:
            if is_expense:
                total_capital -= tr["amount"]
            else:
                total_capital += tr["amount"]
        if tr_date[1] == month and tr_date[2] == year and tr_date[0] <= day:
            if is_expense:
                month_expenses += tr["amount"]
                target = tr["category"].split("::")[-1]
                details[target] = details.get(target, 0.0) + tr["amount"]
            else:
                month_income += tr["amount"]
    return total_capital, month_income, month_expenses, details


def stats_handler(report_date: str) -> str:
    parsed = extract_date(report_date)
    if parsed is None:
        return INCORRECT_DATE_MSG
    day, month, year = parsed
    total_capital, month_income, month_expenses, details = compute_stats(
        day, month, year
    )

    lines = []
    lines.append(f"Your statistics as of {report_date}:")
    lines.append(f"Total capital: {total_capital:.2f} rubles")
    profit = month_income - month_expenses
    if profit >= 0:
        lines.append(f"This month, the profit amounted to {profit:.2f} rubles.")
    else:
        lines.append(f"This month, the loss amounted to {-profit:.2f} rubles.")
    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {month_expenses:.2f} rubles")
    lines.append("")
    lines.append("Details (category: amount):")
    if details:
        sorted_categories = sorted(details.keys())
        for i, cat in enumerate(sorted_categories, 1):
            amt = details[cat]
            amt_str = str(int(amt)) if amt.is_integer() else f"{amt:.2f}"
            lines.append(f"{i}. {cat}: {amt_str}")
    return "\n".join(lines)


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


def main() -> None:
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        command = parts[0]

        if command == "income":
            handle_income(parts)
        elif command == "cost":
            handle_cost(parts)
        elif command == "stats":
            handle_stats(parts)
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()