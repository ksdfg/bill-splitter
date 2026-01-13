from json import dumps

import pytest

from app.schemas.bill import Bill, Item, OCRBill, Outing
from app.services.bill import (
    OutingPaymentBalance,
    PersonBalance,
    calculate_balance,
    calculate_outing_split_with_minimal_transactions,
    get_bill_details_from_image,
)


def test_calculate_balance__simple_bill_split_with_tax_and_service_charge():
    outing = Outing(
        bills=[
            Bill(
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
                amount_paid=990,
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
                amount_paid=862.50,
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


def test_calculate_balance__simple_bill_split_with_tax_and_service_charge__discounted_amount_paid():
    # Same bill as first test, but with a discount applied to amount_paid
    outing = Outing(
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

    balance = calculate_balance(outing)

    assert len(balance.creditors) == 1
    assert balance.creditors[0].name == "bob"
    assert balance.creditors[0].amount == 738.10

    assert len(balance.debtors) == 2
    assert balance.debtors[0].name == "charlie"
    assert balance.debtors[0].amount == 476.19
    assert balance.debtors[1].name == "alice"
    assert balance.debtors[1].amount == 261.90


def test_calculate_balance__multiple_bills_with_different_service_charges_and_no_tax__discounted_amount_paid():
    outing = Outing(
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

    balance = calculate_balance(outing)

    assert len(balance.creditors) == 2

    assert balance.creditors[0].name == "bob"
    assert balance.creditors[0].amount == 293.33
    assert balance.creditors[1].name == "alice"
    assert balance.creditors[1].amount == 253.33

    assert len(balance.debtors) == 1
    assert balance.debtors[0].name == "charlie"
    assert balance.debtors[0].amount == 546.67


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


class TestGetBillDetailsFromImage:
    llm_success_response_text = dumps(
        {
            "tax_rate": 0.05,
            "service_charge": 0.1,
            "amount_paid": 1207.50,
            "items": [
                {
                    "name": "Pizza",
                    "price": 600.0,
                    "quantity": 1,
                },
                {
                    "name": "Coke",
                    "price": 150.0,
                    "quantity": 1,
                },
                {
                    "name": "Ice Cream",
                    "price": 300.0,
                    "quantity": 1,
                },
            ],
        },
        sort_keys=True,
    )
    success_bill = OCRBill.model_validate_json(llm_success_response_text)

    @pytest.fixture
    def _mock_gemini_service_method(self, monkeypatch: pytest.MonkeyPatch):
        outer_self = self

        class MockLLMService:
            def get_bill_details_from_image(self, image_bytes: bytes, mime_type: str) -> str:
                # mirror the original behavior by returning the same JSON text
                return outer_self.llm_success_response_text

        monkeypatch.setattr("app.core.settings.settings.GEMINI_API_KEY", "fake-api-key")
        monkeypatch.setattr("app.services.bill.gemini", MockLLMService())

    def test_gemini(self, _mock_gemini_service_method):
        ocr_bill = get_bill_details_from_image(image_bytes=b"fake-image-bytes", mime_type="image/png")
        assert ocr_bill == self.success_bill

    def test_no_llm_service_set(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("app.services.gemini.settings.GEMINI_API_KEY", None)
        with pytest.raises(ValueError) as exc:
            get_bill_details_from_image(image_bytes=b"fake-image-bytes", mime_type="image/png")
        assert "API key is not set in settings for any LLM." == str(exc.value)
