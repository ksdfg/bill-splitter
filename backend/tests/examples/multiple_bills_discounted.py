# Multiple bills with no tax, different service charges and a discounted amount paid

from app.schemas.bill import Bill, Item, Outing, OutingSplit, Payment, PaymentPlan
from app.services.bill import OutingPaymentBalance, PersonBalance

OUTING = Outing(
    bills=[
        Bill(
            paid_by="alice",
            tax_rate=0,
            service_charge=0.1,
            amount_paid=800,  # discounted from 990
            items=[
                Item(
                    name="Pizza",
                    price=900,
                    quantity=1,
                    consumed_by=["alice", "bob", "charlie"],
                ),
            ],
        ),
        Bill(
            paid_by="bob",
            tax_rate=0,
            service_charge=0.15,
            amount_paid=700.00,  # discounted from 862.50
            items=[
                Item(
                    name="Coffee",
                    price=300,
                    quantity=1,
                    consumed_by=["alice", "charlie"],
                ),
                Item(
                    name="Cake",
                    price=450,
                    quantity=1,
                    consumed_by=["alice", "bob", "charlie"],
                ),
            ],
        ),
    ]
)

OUTING_PAYMENT_BALANCE = OutingPaymentBalance(
    creditors=[
        PersonBalance(name="bob", amount=293.33),
        PersonBalance(name="alice", amount=253.33),
    ],
    debtors=[
        PersonBalance(name="charlie", amount=546.67),
    ],
)

OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS = OutingSplit(
    payment_plans=[
        PaymentPlan(
            name="charlie",
            payments=[
                Payment(to="bob", amount=293.33),
                Payment(to="alice", amount=253.33),
            ],
        ),
    ]
)
