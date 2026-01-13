from collections import defaultdict

from pydantic import BaseModel

from app.core.settings import settings
from app.schemas.bill import OCRBill, Outing, OutingSplit, Payment, PaymentPlan
from app.services import gemini


def get_bill_details_from_image(image_bytes: bytes, mime_type: str) -> OCRBill:
    bill_data: str | None = None

    if settings.GEMINI_API_KEY:
        bill_data = gemini.get_bill_details_from_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
        )
    else:
        raise ValueError("API key is not set in settings for any LLM.")

    return OCRBill.model_validate_json(bill_data)


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
        balance[bill.paid_by] += round(bill.amount_paid, 2)

        # Apply tax and service charge multiplier to the item cost
        additional_charge_rate = 1 + bill.tax_rate + bill.service_charge

        # Calculate total price, and if the amount paid is less than total price, calculate discount applied
        total_price = round(sum(item.price * item.quantity for item in bill.items) * additional_charge_rate, 2)
        discount_rate = round(bill.amount_paid, 2) / total_price
        print(f"Total price: {total_price}, Amount paid: {bill.amount_paid}, Discount rate: {discount_rate}")

        for item in bill.items:
            # Calculate actual cost for the item after applying additional charges and discount
            cost = item.price * item.quantity * additional_charge_rate * discount_rate

            # Split cost equally among consumers and round to avoid floating-point precision issues
            cost_per_person = cost / len(item.consumed_by)

            for consumer in item.consumed_by:
                balance[consumer] -= cost_per_person

    creditors = []
    debtors = []

    for key, value in dict(balance).items():
        if value > 0:
            creditors.append(PersonBalance(name=key, amount=round(value, 2)))
        else:
            debtors.append(PersonBalance(name=key, amount=round(value, 2) * -1))

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
        amount_to_settle = min(debtor.amount, creditor.amount)
        if amount_to_settle > 0:
            all_payments[debtor.name][creditor.name] = amount_to_settle

        # Reduce both balances by the settled amount
        debtor.amount -= amount_to_settle
        creditor.amount -= amount_to_settle

        # Move to the next debtor/creditor once their balance is fully settled
        if round(debtor.amount, 2) == 0:
            debtor_index += 1
        if round(creditor.amount, 2) == 0:
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
