from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.schemas.bill import OCRBill, OutingSplit
from tests import examples


class TestSplit:
    def test_simple_bill_split_with_tax_and_service_charge(self, test_client: TestClient):
        outing_data = examples.simple_with_tax_and_service_charge.OUTING.model_dump()
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 200
        assert (
            OutingSplit.model_validate_json(response.text)
            == examples.simple_with_tax_and_service_charge.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS
        )

    def test_multiple_bills_with_different_service_charges_and_no_tax(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "alice",
                    "tax_rate": 0,
                    "service_charge": 0.1,
                    "amount_paid": 990,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 900,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob", "charlie"],
                        }
                    ],
                },
                {
                    "paid_by": "bob",
                    "tax_rate": 0,
                    "service_charge": 0.15,
                    "amount_paid": 862.50,
                    "items": [
                        {
                            "name": "Coffee",
                            "price": 300,
                            "quantity": 1,
                            "consumed_by": ["alice", "charlie"],
                        },
                        {
                            "name": "Cake",
                            "price": 450,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob", "charlie"],
                        },
                    ],
                },
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 200
        outing_split = response.json()
        assert "payment_plans" in outing_split
        payment_plans = outing_split["payment_plans"]
        assert len(payment_plans) == 1
        payment_plan = payment_plans[0]
        assert "name" in payment_plan
        assert payment_plan["name"] == "charlie"
        assert "payments" in payment_plan
        for payment in payment_plan["payments"]:
            assert "to" in payment
            assert payment["to"] in ["bob", "alice"]
            assert "amount" in payment
            if payment["to"] == "alice":
                assert round(payment["amount"], 2) == 315.00
            elif payment["to"] == "bob":
                assert round(payment["amount"], 2) == 360.00

    def test_simple_bill_split_with_discounted_amount_paid(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1000.00,  # discounted from 1207.50
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob", "charlie"],
                        },
                        {
                            "name": "Coke",
                            "price": 150,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        },
                        {
                            "name": "Ice Cream",
                            "price": 300,
                            "quantity": 1,
                            "consumed_by": ["charlie"],
                        },
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 200
        outing_split = response.json()
        assert "payment_plans" in outing_split
        payment_plans = outing_split["payment_plans"]
        assert len(payment_plans) == 2
        for payment_plan in payment_plans:
            assert "name" in payment_plan
            assert payment_plan["name"] in ["alice", "charlie"]
            assert "payments" in payment_plan
            if payment_plan["name"] == "alice":
                assert len(payment_plan["payments"]) == 1
                assert payment_plan["payments"][0]["to"] == "bob"
                assert round(payment_plan["payments"][0]["amount"], 2) == 261.90
            elif payment_plan["name"] == "charlie":
                assert len(payment_plan["payments"]) == 1
                assert payment_plan["payments"][0]["to"] == "bob"
                assert round(payment_plan["payments"][0]["amount"], 2) == 476.19

    def test_multiple_bills_with_discounts(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "alice",
                    "tax_rate": 0,
                    "service_charge": 0.1,
                    "amount_paid": 800,  # discounted from 990
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 900,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob", "charlie"],
                        }
                    ],
                },
                {
                    "paid_by": "bob",
                    "tax_rate": 0,
                    "service_charge": 0.15,
                    "amount_paid": 700.00,  # discounted from 862.50
                    "items": [
                        {
                            "name": "Coffee",
                            "price": 300,
                            "quantity": 1,
                            "consumed_by": ["alice", "charlie"],
                        },
                        {
                            "name": "Cake",
                            "price": 450,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob", "charlie"],
                        },
                    ],
                },
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 200
        outing_split = response.json()
        assert "payment_plans" in outing_split
        payment_plans = outing_split["payment_plans"]
        assert len(payment_plans) == 1
        payment_plan = payment_plans[0]
        assert "name" in payment_plan
        assert payment_plan["name"] == "charlie"
        assert "payments" in payment_plan
        for payment in payment_plan["payments"]:
            assert "to" in payment
            assert payment["to"] in ["bob", "alice"]
            assert "amount" in payment
            if payment["to"] == "alice":
                assert round(payment["amount"], 2) == 253.33
            elif payment["to"] == "bob":
                assert round(payment["amount"], 2) == 293.33

    def test_outing_with_empty_bills_list(self, test_client: TestClient):
        outing_data = {"bills": []}
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "too_short"
        assert error["loc"] == ["body", "bills"]
        assert error["msg"] == "List should have at least 1 item after validation, not 0"
        assert error["input"] == []
        assert error["ctx"]["field_type"] == "List"
        assert error["ctx"]["min_length"] == 1
        assert error["ctx"]["actual_length"] == 0

    def test_bill_with_empty_items_list(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "too_short"
        assert error["loc"] == ["body", "bills", 0, "items"]
        assert error["msg"] == "List should have at least 1 item after validation, not 0"
        assert error["input"] == []
        assert error["ctx"]["field_type"] == "List"
        assert error["ctx"]["min_length"] == 1
        assert error["ctx"]["actual_length"] == 0

    def test_item_with_empty_name(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "string_too_short"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "name"]
        assert error["msg"] == "String should have at least 1 character"
        assert error["input"] == ""
        assert error["ctx"]["min_length"] == 1

    def test_item_with_zero_price(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 0,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "greater_than"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "price"]
        assert error["msg"] == "Input should be greater than 0"
        assert error["input"] == 0
        assert error["ctx"]["gt"] == 0

    def test_item_with_negative_price(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": -100,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "greater_than"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "price"]
        assert error["msg"] == "Input should be greater than 0"
        assert error["input"] == -100
        assert error["ctx"]["gt"] == 0

    def test_item_with_zero_quantity(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 0,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "greater_than"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "quantity"]
        assert error["msg"] == "Input should be greater than 0"
        assert error["input"] == 0
        assert error["ctx"]["gt"] == 0

    def test_item_with_negative_quantity(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": -5,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "greater_than"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "quantity"]
        assert error["msg"] == "Input should be greater than 0"
        assert error["input"] == -5
        assert error["ctx"]["gt"] == 0

    def test_item_with_empty_consumed_by(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": [],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "too_short"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "consumed_by"]
        assert error["msg"] == "List should have at least 1 item after validation, not 0"
        assert error["input"] == []
        assert error["ctx"]["field_type"] == "List"
        assert error["ctx"]["min_length"] == 1
        assert error["ctx"]["actual_length"] == 0

    def test_bill_with_empty_paid_by(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "string_too_short"
        assert error["loc"] == ["body", "bills", 0, "paid_by"]
        assert error["msg"] == "String should have at least 1 character"
        assert error["input"] == ""
        assert error["ctx"]["min_length"] == 1

    def test_bill_with_negative_tax_rate(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": -0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "greater_than_equal"
        assert error["loc"] == ["body", "bills", 0, "tax_rate"]
        assert error["msg"] == "Input should be greater than or equal to 0"
        assert error["input"] == -0.05
        assert error["ctx"]["ge"] == 0

    def test_bill_with_tax_rate_greater_than_one(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 1.5,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "less_than_equal"
        assert error["loc"] == ["body", "bills", 0, "tax_rate"]
        assert error["msg"] == "Input should be less than or equal to 1"
        assert error["input"] == 1.5
        assert error["ctx"]["le"] == 1

    def test_bill_with_negative_service_charge(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": -0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "greater_than_equal"
        assert error["loc"] == ["body", "bills", 0, "service_charge"]
        assert error["msg"] == "Input should be greater than or equal to 0"
        assert error["input"] == -0.1
        assert error["ctx"]["ge"] == 0

    def test_bill_with_service_charge_greater_than_one(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 1.5,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "less_than_equal"
        assert error["loc"] == ["body", "bills", 0, "service_charge"]
        assert error["msg"] == "Input should be less than or equal to 1"
        assert error["input"] == 1.5
        assert error["ctx"]["le"] == 1

    def test_missing_required_field_bills(self, test_client: TestClient):
        outing_data = {}
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills"]
        assert error["msg"] == "Field required"
        assert error["input"] == {}

    def test_missing_required_field_paid_by(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills", 0, "paid_by"]
        assert error["msg"] == "Field required"

    def test_missing_required_field_items(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills", 0, "items"]
        assert error["msg"] == "Field required"

    def test_missing_required_field_name(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "name"]
        assert error["msg"] == "Field required"

    def test_missing_required_field_price(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "price"]
        assert error["msg"] == "Field required"

    def test_missing_required_field_quantity(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "quantity"]
        assert error["msg"] == "Field required"

    def test_missing_required_field_consumed_by(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "amount_paid": 1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                        }
                    ],
                }
            ]
        }
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        assert len(error_response["detail"]) == 1
        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills", 0, "items", 0, "consumed_by"]
        assert error["msg"] == "Field required"

    def test_missing_required_field_amount_paid(self, test_client: TestClient):
        outing_data = {
            "bills": [
                {
                    "paid_by": "bob",
                    "tax_rate": 0.05,
                    "service_charge": 0.1,
                    "items": [
                        {
                            "name": "Pizza",
                            "price": 600,
                            "quantity": 1,
                            "consumed_by": ["alice", "bob"],
                        }
                    ],
                }
            ]
        }

        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422

        error_response = response.json()

        assert "detail" in error_response
        assert len(error_response["detail"]) == 1

        error = error_response["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "bills", 0, "amount_paid"]
        assert error["msg"] == "Field required"


class TestExtractBillDetailsFromImage:
    success_bill = examples.simple_with_tax_and_service_charge.OCR_BILL

    @pytest.fixture
    def mock_bill_service_method(self, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
        def mock_get_bill_details_from_image(image_bytes: bytes, mime_type: str) -> OCRBill:
            return self.success_bill

        monkeypatch.setattr("app.core.settings.settings.GEMINI_API_KEY", None)
        monkeypatch.setattr("app.api.v1.endpoints.bill.get_bill_details_from_image", mock_get_bill_details_from_image)
        yield None

    def test_valid_image_file(self, test_client, mock_bill_service_method: None):
        files = {"file": ("test_image.png", b"dummy image content", "image/png")}
        response = test_client.post("/api/v1/bills/ocr", files=files)
        assert response.status_code == 200
        ocr_response = response.text
        assert OCRBill.model_validate_json(ocr_response) == self.success_bill

    def test_invalid_file_type(self, test_client: TestClient):
        files = {"file": ("test.txt", b"dummy content", "text/plain")}
        response = test_client.post("/api/v1/bills/ocr", files=files)
        assert response.status_code == 400
        error_response = response.json()
        assert "detail" in error_response
        assert error_response["detail"] == "Invalid file type. Please upload an image file."
        assert error_response == {"detail": "Invalid file type. Please upload an image file."}

    def test_no_file(self, test_client: TestClient):
        response = test_client.post("/api/v1/bills/ocr", files={})
        assert response.status_code == 422
        error_response = response.json()
        assert error_response == {
            "detail": [{"type": "missing", "loc": ["body", "file"], "msg": "Field required", "input": None}]
        }
