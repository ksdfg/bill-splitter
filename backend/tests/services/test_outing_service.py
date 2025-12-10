from app.schemas.outing import Bill, Item, Outing
from app.services.outing import (
    OutingPaymentBalance,
    PersonBalance,
    calculate_balance,
    calculate_outing_split_with_minimal_transactions,
)


def test_calculate_balance__simple_bill_split_with_tax_and_service_charge():
    outing = Outing(
        bills=[
            Bill(
                paid_by="Bob",
                tax_rate=0.05,
                service_charge=0.1,
                items=[
                    Item(
                        name="Pizza",
                        price=600,
                        quantity=1,
                        consumed_by=["Alice", "Bob", "Charlie"],
                    ),
                    Item(
                        name="Coke",
                        price=150,
                        quantity=1,
                        consumed_by=["Alice", "Bob"],
                    ),
                    Item(
                        name="Ice Cream",
                        price=300,
                        quantity=1,
                        consumed_by=["Charlie"],
                    ),
                ],
            )
        ]
    )

    balance = calculate_balance(outing)

    assert len(balance.creditors) == 1
    assert balance.creditors[0].name == "Bob"
    assert round(balance.creditors[0].amount, 2) == 891.25

    assert len(balance.debtors) == 2
    assert balance.debtors[0].name == "Charlie"
    assert round(balance.debtors[0].amount, 2) == 575.00
    assert balance.debtors[1].name == "Alice"
    assert round(balance.debtors[1].amount, 2) == 316.25


def test_calculate_balance__multiple_bills_with_different_service_charges_and_no_tax():
    outing = Outing(
        bills=[
            Bill(
                paid_by="Alice",
                tax_rate=0,
                service_charge=0.1,
                items=[
                    Item(
                        name="Pizza",
                        price=900,
                        quantity=1,
                        consumed_by=["Alice", "Bob", "Charlie"],
                    ),
                ],
            ),
            Bill(
                paid_by="Bob",
                tax_rate=0,
                service_charge=0.15,
                items=[
                    Item(
                        name="Coffee",
                        price=300,
                        quantity=1,
                        consumed_by=["Alice", "Charlie"],
                    ),
                    Item(
                        name="Cake",
                        price=450,
                        quantity=1,
                        consumed_by=["Alice", "Bob", "Charlie"],
                    ),
                ],
            ),
        ]
    )

    balance = calculate_balance(outing)

    assert len(balance.creditors) == 2
    assert balance.creditors[0].name == "Bob"
    assert round(balance.creditors[0].amount, 2) == 360.00
    assert balance.creditors[1].name == "Alice"
    assert round(balance.creditors[1].amount, 2) == 315.00

    assert len(balance.debtors) == 1
    assert balance.debtors[0].name == "Charlie"
    assert round(balance.debtors[0].amount, 2) == 675.00


def test_calculate_outing_split_with_minimal_transactions__simple_bill_split_with_tax_and_service_charge():
    balance = OutingPaymentBalance(
        creditors=[PersonBalance(name="Bob", amount=891.25)],
        debtors=[PersonBalance(name="Charlie", amount=575), PersonBalance(name="Alice", amount=316.25)],
    )

    split = calculate_outing_split_with_minimal_transactions(balance)

    assert len(split.payment_plans) == 2
    for payment_plan in split.payment_plans:
        assert payment_plan.name in ["Charlie", "Alice"]
        if payment_plan.name == "Charlie":
            assert len(payment_plan.payments) == 1
            assert payment_plan.payments[0].to == "Bob"
            assert round(payment_plan.payments[0].amount, 2) == 575.00
        elif payment_plan.name == "Alice":
            assert len(payment_plan.payments) == 1
            assert payment_plan.payments[0].to == "Bob"
            assert round(payment_plan.payments[0].amount, 2) == 316.25


def test_calculate_outing_split_with_minimal_transactions__multiple_bills_with_different_service_charges_and_no_tax():
    balance = OutingPaymentBalance(
        creditors=[
            PersonBalance(name="Bob", amount=360),
            PersonBalance(name="Alice", amount=315),
        ],
        debtors=[
            PersonBalance(name="Charlie", amount=675),
        ],
    )

    split = calculate_outing_split_with_minimal_transactions(balance)

    assert len(split.payment_plans) == 1
    payment_plan = split.payment_plans[0]
    assert payment_plan.name == "Charlie"
    assert len(payment_plan.payments) == 2
    for payment in payment_plan.payments:
        assert payment.to in ["Bob", "Alice"]
        if payment.to == "Bob":
            assert round(payment.amount, 2) == 360.00
        elif payment.to == "Alice":
            assert round(payment.amount, 2) == 315.00
