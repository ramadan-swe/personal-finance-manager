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
    def _fmt(d):
        if isinstance(d, Decimal):
            return float(d.quantize(Decimal("0.01")))
        return d  # type: ignore

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





def generate_financial_health_score(user_id: str, transactions: Optional[List[Transaction]] = None) -> dict:
    """Generate a financial health score based on all transactions for a given user.

    Args:
        user_id: username / id of the user
        transactions: optional list of Transaction objects to use (for testing); if None, fetched from TransactionManager

    Returns:
        dict with keys: total_income, total_expense, net_savings, savings_ratio, financial_health_score, status
    """
    if transactions is None:
        tm = TransactionManager(DataPersistenceService())
        transactions = tm.get_all_transactions(user_id)

    total_income = Decimal(0)
    total_expenses = Decimal(0)

    for t in transactions:
        amt = _to_decimal(t.amount)
        if t.type == "income":
            total_income += amt
        else:
            total_expenses += amt

    net_savings = total_income - total_expenses

    savings_ratio = Decimal(0)
    if total_income > 0:
        savings_ratio = (net_savings / total_income) * 100

    # Clamp function
    def clamp(n, minn, maxn):
        return max(minn, min(n, maxn))

    # Continuous scoring formula: score = clamp(50 + 2.5 * savings_ratio, 0, 100)
    financial_health_score = clamp(50 + (Decimal("2.5") * savings_ratio), Decimal(0), Decimal(100))

    status = ""
    if financial_health_score >= 90:
        status = "Excellent"
    elif financial_health_score >= 70:
        status = "Good"
    elif financial_health_score >= 50:
        status = "Fair"
    elif financial_health_score >= 30:
        status = "Poor"
    else:
        status = "Very Poor"

    # Convert Decimal values to floats for easier display/storage (keeping 2 decimals)
    def _fmt(d):
        if isinstance(d, Decimal):
            return float(d.quantize(Decimal("0.01")))
        return d  # type: ignore

    return {
        "total_income": _fmt(total_income),
        "total_expense": _fmt(total_expenses),
        "net_savings": _fmt(net_savings),
        "savings_ratio": _fmt(savings_ratio),
        "financial_health_score": _fmt(financial_health_score),
        "status": status,
    }
