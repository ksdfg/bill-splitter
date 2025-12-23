from app.schemas.bill import Bill, Item, Outing
from app.services.bill import (
    OutingPaymentBalance,
    PersonBalance,
    calculate_balance,
    calculate_outing_split_with_minimal_transactions,
)


def test_calculate_balance__simple_bill_split_with_tax_and_service_charge():
    outing = Outing(
        bills=[
            Bill(
                paid_by="bob",
                tax_rate=0.05,
                service_charge=0.1,
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

    balance = calculate_balance(outing)

    assert len(balance.creditors) == 1
    assert balance.creditors[0].name == "bob"
    assert round(balance.creditors[0].amount, 2) == 891.25

    assert len(balance.debtors) == 2
    assert balance.debtors[0].name == "charlie"
    assert round(balance.debtors[0].amount, 2) == 575.00
    assert balance.debtors[1].name == "alice"
    assert round(balance.debtors[1].amount, 2) == 316.25


def test_calculate_balance__multiple_bills_with_different_service_charges_and_no_tax():
    outing = Outing(
        bills=[
            Bill(
                paid_by="alice",
                tax_rate=0,
                service_charge=0.1,
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

    balance = calculate_balance(outing)

    assert len(balance.creditors) == 2
    assert balance.creditors[0].name == "bob"
    assert round(balance.creditors[0].amount, 2) == 360.00
    assert balance.creditors[1].name == "alice"
    assert round(balance.creditors[1].amount, 2) == 315.00

    assert len(balance.debtors) == 1
    assert balance.debtors[0].name == "charlie"
    assert round(balance.debtors[0].amount, 2) == 675.00


def test_calculate_outing_split_with_minimal_transactions__simple_bill_split_with_tax_and_service_charge():
    balance = OutingPaymentBalance(
        creditors=[PersonBalance(name="bob", amount=891.25)],
        debtors=[PersonBalance(name="charlie", amount=575), PersonBalance(name="alice", amount=316.25)],
    )

    split = calculate_outing_split_with_minimal_transactions(balance)

    assert len(split.payment_plans) == 2
    for payment_plan in split.payment_plans:
        assert payment_plan.name in ["charlie", "alice"]
        if payment_plan.name == "charlie":
            assert len(payment_plan.payments) == 1
            assert payment_plan.payments[0].to == "bob"
            assert round(payment_plan.payments[0].amount, 2) == 575.00
        elif payment_plan.name == "alice":
            assert len(payment_plan.payments) == 1
            assert payment_plan.payments[0].to == "bob"
            assert round(payment_plan.payments[0].amount, 2) == 316.25


def test_calculate_outing_split_with_minimal_transactions__multiple_bills_with_different_service_charges_and_no_tax():
    balance = OutingPaymentBalance(
        creditors=[
            PersonBalance(name="bob", amount=360),
            PersonBalance(name="alice", amount=315),
        ],
        debtors=[
            PersonBalance(name="charlie", amount=675),
        ],
    )

    split = calculate_outing_split_with_minimal_transactions(balance)

    assert len(split.payment_plans) == 1
    payment_plan = split.payment_plans[0]
    assert payment_plan.name == "charlie"
    assert len(payment_plan.payments) == 2
    for payment in payment_plan.payments:
        assert payment.to in ["bob", "alice"]
        if payment.to == "bob":
            assert round(payment.amount, 2) == 360.00
        elif payment.to == "alice":
            assert round(payment.amount, 2) == 315.00
