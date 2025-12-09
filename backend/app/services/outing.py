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
    """
    Calculate how much each person in the outing owes / is owed.

    :param outing: Contains the bills of the outing
    :return: List of creditors and debtors
    """
    balance = defaultdict(float)

    for bill in outing.bills:
        total_price = 0.0

        for item in bill.items:
            # Apply tax and service charge multiplier to the item cost
            additional_charge_rate = 1 + bill.tax_rate + bill.service_charge
            cost = item.price * item.quantity * additional_charge_rate

            total_price += cost
            # Split cost equally among consumers and round to avoid floating-point precision issues
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

    # Sort by amount descending to match largest debts/credits first for optimal settlement
    creditors.sort(key=lambda x: x.amount, reverse=True)
    debtors.sort(key=lambda x: x.amount, reverse=True)

    return OutingPaymentBalance(creditors=creditors, debtors=debtors)


def calculate_outing_split_with_minimal_transactions(
    balance: OutingPaymentBalance,
) -> OutingSplit:
    """
    Calculate the minimal number of transactions needed to settle all debts.

    This function uses a greedy algorithm to match debtors with creditors,
    settling debts in the order of largest amounts first. It minimizes the
    number of transactions by matching debtors and creditors until all balances
    are settled to zero.

    :param balance: Contains lists of creditors and debtors with their amounts
    :return: An OutingSplit containing a list of payment plans for each debtor
    """
    all_payments = defaultdict(lambda: defaultdict(float))

    debtor_index = 0
    creditor_index = 0

    while debtor_index < len(balance.debtors) and creditor_index < len(balance.creditors):
        debtor = balance.debtors[debtor_index]
        creditor = balance.creditors[creditor_index]

        # Match the smaller of the two amounts to settle as much as possible in one transaction
        amount_to_settle = round(min(debtor.amount, creditor.amount), 2)
        if amount_to_settle > 0:
            all_payments[debtor.name][creditor.name] = amount_to_settle

        # Reduce both balances by the settled amount
        debtor.amount -= amount_to_settle
        creditor.amount -= amount_to_settle

        # Move to the next debtor/creditor once their balance is fully settled
        if debtor.amount == 0:
            debtor_index += 1
        if creditor.amount == 0:
            creditor_index += 1

    return OutingSplit(
        payment_plans=[
            PaymentPlan(
                name=name,
                payments=[Payment(to=to, amount=amount) for to, amount in payments.items()],
            )
            for name, payments in all_payments.items()
        ]
    )
