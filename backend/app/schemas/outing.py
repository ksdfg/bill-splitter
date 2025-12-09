from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    price: float
    quantity: int
    consumed_by: list[str]


class Bill(BaseModel):
    items: list[Item]
    paid_by: str
    tax_rate: float = Field(default=0.05)
    service_charge: float = Field(default=0.0)


class Outing(BaseModel):
    bills: list[Bill]


class Payment(BaseModel):
    to: str
    amount: float


class PaymentPlan(BaseModel):
    name: str
    payments: list[Payment]


class OutingSplit(BaseModel):
    payment_plans: list[PaymentPlan]
