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
