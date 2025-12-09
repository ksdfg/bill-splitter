from collections import defaultdict

from pydantic import BaseModel

from app.schemas.outing import Outing, OutingSplit, Payment, PaymentPlan


class PersonBalance(BaseModel):
    name: str
    amount: float


class OutingPaymentBalance(BaseModel):
    creditors: list[PersonBalance]
    debtors: list[PersonBalance]


def calculate_balance(outing: Outing) -> OutingPaymentBalance:
    balance = defaultdict(float)

    for bill in outing.bills:
        total_price = 0.0

        for item in bill.items:
            additional_charge_rate = 1 + bill.tax_rate + bill.service_charge
            cost = item.price * item.quantity * additional_charge_rate

            total_price += cost
            cost_per_person = round(cost / len(item.consumed_by), 2)

            for consumer in item.consumed_by:
                balance[consumer] -= cost_per_person

        balance[bill.paid_by] += total_price

    creditors = []
    debtors = []

    for key, value in dict(balance).items():
        if value > 0:
            creditors.append(PersonBalance(name=key, amount=value))
        else:
            debtors.append(PersonBalance(name=key, amount=value * -1))

    creditors.sort(key=lambda x: x.amount, reverse=True)
    debtors.sort(key=lambda x: x.amount, reverse=True)

    return OutingPaymentBalance(creditors=creditors, debtors=debtors)


def calculate_outing_split_with_minimal_transactions(
    balance: OutingPaymentBalance,
) -> OutingSplit:
    all_payments = defaultdict(lambda: defaultdict(float))

    debtor_index = 0
    creditor_index = 0

    while debtor_index < len(balance.debtors) and creditor_index < len(
        balance.creditors
    ):
        debtor = balance.debtors[debtor_index]
        creditor = balance.creditors[creditor_index]

        amount_to_settle = round(min(debtor.amount, creditor.amount), 2)
        if amount_to_settle > 0:
            all_payments[debtor.name][creditor.name] = amount_to_settle

        debtor.amount -= amount_to_settle
        creditor.amount -= amount_to_settle

        if debtor.amount == 0:
            debtor_index += 1
        if creditor.amount == 0:
            creditor_index += 1

    return OutingSplit(
        payment_plans=[
            PaymentPlan(
                name=name,
                payments=[
                    Payment(to=to, amount=amount)
                    for to, amount in payments.items()
                ],
            )
            for name, payments in all_payments.items()
        ]
    )
