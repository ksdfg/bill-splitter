from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0.0)
    quantity: int = Field(gt=0)
    consumed_by: list[str] = Field(min_length=1)


class Bill(BaseModel):
    items: list[Item] = Field(min_length=1)
    paid_by: str = Field(min_length=1)
    tax_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    service_charge: float = Field(default=0.0, ge=0.0, le=1.0)


class Outing(BaseModel):
    bills: list[Bill] = Field(min_length=1)


class Payment(BaseModel):
    to: str = Field(min_length=1)
    amount: float = Field(gt=0.0)


class PaymentPlan(BaseModel):
    name: str = Field(min_length=1)
    payments: list[Payment] = Field(min_length=1)


class OutingSplit(BaseModel):
    payment_plans: list[PaymentPlan]
