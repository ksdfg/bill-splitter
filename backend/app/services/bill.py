from collections import defaultdict

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.settings import settings
from app.schemas.bill import OCRBill, Outing, OutingSplit, Payment, PaymentPlan
from app.services.gemini import generate_content_from_image

BILL_OCR_PROMPT = """
You are an expert at extracting information from bills and receipts.
Your task is to analyze the provided image of a bill and extract the following information in JSON format:

Extract a Bill object with the following structure:
- items: A list of items, where each item contains:
  - name: The name of the item (string, non-empty)
  - price: The price of the item (float, must be positive)
  - quantity: The quantity ordered (integer, must be positive)
- tax_rate: The tax rate applied to the bill as a decimal (float, between 0.0 and 1.0, default is 0.0 if not found)
- service_charge: The service charge as a decimal (float, between 0.0 and 1.0, default is 0.0 if not found)
- amount_paid: The final total amount that must be paid, after applying all tax, service charges and discounts (float, must be positive)

Important notes:
- Extract only the items that appear on the bill
- Calculate tax_rate and service_charge from the bill if visible, otherwise use defaults
- Ensure all extracted values match the specified types and constraints
- Return the response as valid JSON that matches the Bill schema

Please analyze the bill image and extract the information now.
"""


GENERATE_CONTENT_CONFIG = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=genai.types.Schema(
        type=genai.types.Type.OBJECT,
        properties={
            "tax_rate": genai.types.Schema(
                type=genai.types.Type.NUMBER,
            ),
            "service_charge": genai.types.Schema(
                type=genai.types.Type.NUMBER,
            ),
            "items": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    properties={
                        "name": genai.types.Schema(
                            type=genai.types.Type.STRING,
                        ),
                        "price": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                        "quantity": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                    },
                ),
            ),
        },
    ),
)


def get_bill_details_from_image(image_bytes: bytes, mime_type: str) -> OCRBill:
    if settings.GEMINI_API_KEY:
        bill_data = generate_content_from_image(
            prompt=BILL_OCR_PROMPT,
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
