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


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split('-')
    if len(parts) != 3:
        return None
    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None

    if month < 1 or month > 12:
        return None

    if month == 2:
        max_day = 29 if is_leap_year(year) else 28
    elif month in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 31

    if day < 1 or day > max_day:
        return None

    return (day, month, year)


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append(
        {"category": category_name, "amount": amount, "date": income_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines = []
    for common, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            lines.append(f"{common}::{target}")
    lines.sort()
    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    day, month, year = extract_date(report_date)

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    details = {}

    for tr in financial_transactions_storage:
        tr_day, tr_month, tr_year = extract_date(tr["date"])
        tr_tuple = (tr_year, tr_month, tr_day)
        report_tuple = (year, month, day)

        if tr_tuple <= report_tuple:
            if "category" in tr:
                total_capital -= tr["amount"]
            else:
                total_capital += tr["amount"]

        if tr_year == year and tr_month == month and tr_day <= day:
            if "category" in tr:
                month_expenses += tr["amount"]
                target = tr["category"].split("::")[-1]
                details[target] = details.get(target, 0) + tr["amount"]
            else:
                month_income += tr["amount"]

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
            if amt.is_integer():
                amt_str = str(int(amt))
            else:
                amt_str = f"{amt:.2f}"
            lines.append(f"{i}. {cat}: {amt_str}")

    return "\n".join(lines)


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
            if len(parts) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount_str = parts[1]
            date_str = parts[2]

            try:
                amount = float(amount_str.replace(',', '.'))
            except ValueError:
                print(NONPOSITIVE_VALUE_MSG)
                continue
            if amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            if extract_date(date_str) is None:
                print(INCORRECT_DATE_MSG)
                continue

            print(income_handler(amount, date_str))

        elif command == "cost":
            if len(parts) == 2 and parts[1] == "categories":
                print(cost_categories_handler())
                continue

            if len(parts) != 4:
                print(UNKNOWN_COMMAND_MSG)
                continue

            category_name = parts[1]
            amount_str = parts[2]
            date_str = parts[3]

            try:
                amount = float(amount_str.replace(',', '.'))
            except ValueError:
                print(NONPOSITIVE_VALUE_MSG)
                continue
            if amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            if "::" not in category_name:
                print(NOT_EXISTS_CATEGORY)
                print(cost_categories_handler())
                continue

            common, target = category_name.split("::", 1)
            if common not in EXPENSE_CATEGORIES or target not in EXPENSE_CATEGORIES[common]:
                print(NOT_EXISTS_CATEGORY)
                print(cost_categories_handler())
                continue

            if extract_date(date_str) is None:
                print(INCORRECT_DATE_MSG)
                continue

            print(cost_handler(category_name, amount, date_str))

        elif command == "stats":
            if len(parts) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue

            date_str = parts[1]
            if extract_date(date_str) is None:
                print(INCORRECT_DATE_MSG)
                continue

            print(stats_handler(date_str))

        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()