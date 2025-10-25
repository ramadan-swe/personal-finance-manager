from enum import Enum
from decimal import Decimal

class Currency:
    def __init__(self, short_name, symbol):
        self.short_name = short_name
        self.symbol = symbol

    def to_dict(self):
        return {"short_name": self.short_name, "symbol": self.symbol}

    @classmethod
    def from_dict(cls, data):
        return cls(data["short_name"], data["symbol"])

class Currencies:
    USD = Currency("USD", "$")
    EUR = Currency("EUR", "€")
    GBP = Currency("GBP", "£")
    JPY = Currency("JPY", "¥")
    EGP = Currency("EGP", "E£")

    @classmethod
    def get_currencies(cls):
        return [cls.USD, cls.EUR, cls.GBP, cls.JPY, cls.EGP]

    @classmethod
    def from_short_name(cls, short_name):
        for currency in cls.get_currencies():
            if currency.short_name == short_name:
                return currency
        return None

class PaymentMethod(Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    CASH = "cash"

class Transaction:
    def __init__(self, amount, date, type, description, category, user_id, payment_method, currency, id=None):
        self.id = id
        self.amount = Decimal(str(amount))
        self.date = date # Store as ISO format string YYYY-MM-DD
        self.type = type # "income" or "expense"
        self.description = description
        self.category = category
        self.user_id = user_id
        self.payment_method = payment_method
        self.currency = currency

    def to_dict(self, target='json'):
        d = {
            "id": self.id,
            "amount": float(self.amount),
            "date": self.date,
            "type": self.type,
            "description": self.description,
            "category": self.category,
            "user_id": self.user_id,
            "payment_method": self.payment_method.value if self.payment_method else None,
        }
        if target == 'csv':
            d['currency'] = self.currency.short_name if self.currency else None
        else: # json
            d['currency'] = self.currency.to_dict() if self.currency else None
        return d

    @classmethod
    def from_dict(cls, data):
        currency_val = data.get('currency')
        currency = None
        if isinstance(currency_val, dict):
            currency = Currency.from_dict(currency_val)
        elif isinstance(currency_val, str):
            currency = Currencies.from_short_name(currency_val)

        payment_method_str = data.get("payment_method")
        payment_method = None
        if payment_method_str:
            try:
                payment_method = PaymentMethod(payment_method_str)
            except ValueError:
                payment_method = None

        return cls(
            amount=Decimal(str(data["amount"])),
            date=data["date"],
            type=data["type"],
            description=data["description"],
            category=data["category"],
            user_id=data.get("user_id"),
            payment_method=payment_method,
            currency=currency,
            id=data.get("id")
        )
