from decimal import Decimal, getcontext
from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from src.services.data_persistence import DataPersistenceService
from src.services.transaction_manager import TransactionManager
from src.models.transaction import Transaction

getcontext().prec = 28


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(0)


def generate_monthly_report(user_id: str, year: int, month: int, categories: Optional[List[str]] = None, transactions: Optional[List[Transaction]] = None) -> dict:
    """Generate a monthly financial report for a given user.

    Args:
        user_id: username / id of the user
        year: year as int (e.g., 2025)
        month: month as int (1-12)
        categories: optional list of categories to filter (None = include all)
        transactions: optional list of Transaction objects to use (for testing); if None, fetched from TransactionManager

    Returns:
        dict with keys: month, year, income, expenses, savings, category_breakdown (dict)
    """
    if transactions is None:
        tm = TransactionManager(DataPersistenceService())
        transactions = tm.get_all_transactions(user_id)

    # Filter by year/month and optional categories
    filtered = []
    for t in transactions:
        try:
            dt = datetime.fromisoformat(t.date)
        except Exception:
            # Skip malformed dates
            continue
        if dt.year == year and dt.month == month:
            if categories is None or (t.category in categories):
                filtered.append(t)

    income = Decimal(0)
    expenses = Decimal(0)
    breakdown = defaultdict(lambda: {"income": Decimal(0), "expenses": Decimal(0), "count": 0})

    for t in filtered:
        amt = _to_decimal(t.amount)
        cat = t.category if t.category else "Uncategorized"
        if t.type == "income":
            income += amt
            breakdown[cat]["income"] += amt
        else:
            expenses += amt
            breakdown[cat]["expenses"] += amt
        breakdown[cat]["count"] += 1

    savings = income - expenses

    # Convert Decimal values to floats for easier display/storage (keeping 2 decimals)
    def _fmt(d: Decimal):
        return float(d.quantize(Decimal("0.01")))

    breakdown_out = {}
    for cat, vals in breakdown.items():
        breakdown_out[cat] = {"income": _fmt(vals["income"]), "expenses": _fmt(vals["expenses"]), "count": vals["count"]}

    return {
        "year": year,
        "month": month,
        "income": _fmt(income),
        "expenses": _fmt(expenses),
        "savings": _fmt(savings),
        "category_breakdown": breakdown_out,
        "transactions_count": len(filtered),
    }


def generate_dashboard_summary(user_id: str, months: int = 3, transactions: Optional[List[Transaction]] = None) -> dict:
    """Generate a simple dashboard summary over the last `months` months.

    This returns monthly totals for income/expenses and an overall category top-5 breakdown.
    """
    if transactions is None:
        tm = TransactionManager(DataPersistenceService())
        transactions = tm.get_all_transactions(user_id)

    # Group by year-month
    monthly = defaultdict(lambda: {"income": Decimal(0), "expenses": Decimal(0)})
    category_totals = defaultdict(Decimal)

    for t in transactions:
        try:
            dt = datetime.fromisoformat(t.date)
        except Exception:
            continue
        key = f"{dt.year:04d}-{dt.month:02d}"
        amt = _to_decimal(t.amount)
        cat = t.category if t.category else "Uncategorized"
        if t.type == "income":
            monthly[key]["income"] += amt
        else:
            monthly[key]["expenses"] += amt
            category_totals[cat] += amt

    # Sort months most recent first
    sorted_months = sorted(monthly.keys(), reverse=True)[:months]
    monthly_out = [{"month": m, "income": float(monthly[m]["income"].quantize(Decimal("0.01"))), "expenses": float(monthly[m]["expenses"].quantize(Decimal("0.01")))} for m in sorted_months]

    # Top categories (by expense)
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    top_categories_out = [{"category": k, "amount": float(v.quantize(Decimal("0.01")))} for k, v in top_categories]

    return {
        "monthly": monthly_out,
        "top_categories": top_categories_out,
    }
