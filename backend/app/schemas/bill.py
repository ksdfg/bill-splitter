from pydantic import BaseModel, Field, field_validator


class OCRBillItem(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0.0)
    quantity: int = Field(gt=0)


class OCRBill(BaseModel):
    items: list[OCRBillItem]
    tax_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    service_charge: float = Field(default=0.0, ge=0.0, le=1.0)


class Item(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0.0)
    quantity: int = Field(gt=0)
    consumed_by: list[str] = Field(min_length=1)

    @field_validator("consumed_by", mode="after")
    @classmethod
    def to_lower(cls, value):
        return [v.lower() for v in value]


class Bill(BaseModel):
    items: list[Item] = Field(min_length=1)
    paid_by: str = Field(min_length=1)
    amount_paid: float = Field(gt=0.0)
    tax_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    service_charge: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("paid_by", mode="after")
    @classmethod
    def to_lower(cls, value):
        return value.lower()


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
