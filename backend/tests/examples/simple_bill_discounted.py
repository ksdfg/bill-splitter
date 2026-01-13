# SimplebBill with tax, service charge and a discounted amount paid

from app.schemas.bill import Bill, Item, Outing, OutingSplit, Payment, PaymentPlan
from app.services.bill import OutingPaymentBalance, PersonBalance

OUTING = Outing(
    bills=[
        Bill(
            paid_by="bob",
            tax_rate=0.05,
            service_charge=0.1,
            amount_paid=1000.00,  # discounted from 1207.50
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
    ]
)

OUTING_PAYMENT_BALANCE = OutingPaymentBalance(
    creditors=[
        PersonBalance(name="bob", amount=738.10),
    ],
    debtors=[
        PersonBalance(name="charlie", amount=476.19),
        PersonBalance(name="alice", amount=261.90),
    ],
)

OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS = OutingSplit(
    payment_plans=[
        PaymentPlan(name="charlie", payments=[Payment(to="bob", amount=476.19)]),
        PaymentPlan(name="alice", payments=[Payment(to="bob", amount=261.90)]),
    ]
)
