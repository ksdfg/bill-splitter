from app.schemas.bill import Bill, Item, OCRBill, OCRBillItem, Outing, OutingSplit, Payment, PaymentPlan
from app.services.bill import OutingPaymentBalance, PersonBalance

OCR_BILL = OCRBill(
    tax_rate=0.05,
    service_charge=0.1,
    amount_paid=1207.50,
    items=[
        OCRBillItem(
            name="Pizza",
            price=600,
            quantity=1,
        ),
        OCRBillItem(
            name="Coke",
            price=150,
            quantity=1,
        ),
        OCRBillItem(
            name="Ice Cream",
            price=300,
            quantity=1,
        ),
    ],
)

BILL = Bill(
    paid_by="bob",
    tax_rate=0.05,
    service_charge=0.1,
    amount_paid=1207.50,
    items=[
        Item(
            name="Pizza",
            price=600,
            quantity=1,
            consumed_by=["alice", "bob", "charlie"],
        ),
        Item(
            name="Coke",
            price=150,
            quantity=1,
            consumed_by=["alice", "bob"],
        ),
        Item(
            name="Ice Cream",
            price=300,
            quantity=1,
            consumed_by=["charlie"],
        ),
    ],
)

OUTING = Outing(bills=[BILL])

OUTING_PAYMENT_BALANCE = OutingPaymentBalance(
    creditors=[PersonBalance(name="bob", amount=891.25)],
    debtors=[PersonBalance(name="charlie", amount=575), PersonBalance(name="alice", amount=316.25)],
)

OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS = OutingSplit(
    payment_plans=[
        PaymentPlan(name="charlie", payments=[Payment(to="bob", amount=575.0)]),
        PaymentPlan(name="alice", payments=[Payment(to="bob", amount=316.25)]),
    ]
)
