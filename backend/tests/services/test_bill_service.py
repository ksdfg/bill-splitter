import pytest

from app.schemas.bill import Outing, OutingSplit
from app.services.bill import (
    OutingPaymentBalance,
    calculate_balance,
    calculate_outing_split_with_minimal_transactions,
    get_bill_details_from_image,
)
from tests import examples


class TestCalculateBalance:
    @pytest.mark.parametrize(
        "outing, balance",
        [
            (
                examples.simple_bill.OUTING,
                examples.simple_bill.OUTING_PAYMENT_BALANCE,
            ),
            (
                examples.multiple_bills.OUTING,
                examples.multiple_bills.OUTING_PAYMENT_BALANCE,
            ),
            (
                examples.simple_bill_discounted.OUTING,
                examples.simple_bill_discounted.OUTING_PAYMENT_BALANCE,
            ),
            (
                examples.multiple_bills_discounted.OUTING,
                examples.multiple_bills_discounted.OUTING_PAYMENT_BALANCE,
            ),
        ],
    )
    def test_examples(self, outing: Outing, balance: OutingPaymentBalance):
        assert calculate_balance(outing) == balance


class TestCalculateOutingSplitWithMinimalTransactions:
    @pytest.mark.parametrize(
        "balance, split",
        [
            (
                examples.simple_bill.OUTING_PAYMENT_BALANCE,
                examples.simple_bill.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
            (
                examples.multiple_bills.OUTING_PAYMENT_BALANCE,
                examples.multiple_bills.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
            (
                examples.simple_bill_discounted.OUTING_PAYMENT_BALANCE,
                examples.simple_bill_discounted.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
            (
                examples.multiple_bills_discounted.OUTING_PAYMENT_BALANCE,
                examples.multiple_bills_discounted.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
        ],
    )
    def test_examples(self, balance: OutingPaymentBalance, split: OutingSplit):
        assert calculate_outing_split_with_minimal_transactions(balance) == split


class TestGetBillDetailsFromImage:
    success_bill = examples.simple_bill.OCR_BILL
    llm_success_response_text = success_bill.model_dump_json()

    @pytest.fixture
    def _mock_litellm_service_method(self, monkeypatch: pytest.MonkeyPatch):
        outer_self = self

        class MockLLMService:
            def get_bill_details_from_image(self, image_bytes: bytes, mime_type: str) -> str:
                return outer_self.llm_success_response_text

        monkeypatch.setattr("app.services.bill.litellm_service", MockLLMService())

    def test_litellm(self, _mock_litellm_service_method):
        ocr_bill = get_bill_details_from_image(image_bytes=b"fake-image-bytes", mime_type="image/png")
        assert ocr_bill == self.success_bill
