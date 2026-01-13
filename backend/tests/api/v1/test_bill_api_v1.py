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

    @pytest.mark.parametrize(
        "outing_data, error_response",
        [
            # Missing bills field
            ({}, {"detail": [{"type": "missing", "loc": ["body", "bills"], "msg": "Field required", "input": {}}]}),
            # Empty bills list
            (
                {"bills": []},
                {
                    "detail": [
                        {
                            "type": "too_short",
                            "loc": ["body", "bills"],
                            "msg": "List should have at least 1 item after validation, not 0",
                            "input": [],
                            "ctx": {"field_type": "List", "min_length": 1, "actual_length": 0},
                        }
                    ]
                },
            ),
            # Empty items list
            (
                {
                    "bills": [
                        {
                            "paid_by": "bob",
                            "tax_rate": 0.05,
                            "service_charge": 0.1,
                            "amount_paid": 1,
                            "items": [],
                        }
                    ]
                },
                {
                    "detail": [
                        {
                            "type": "too_short",
                            "loc": ["body", "bills", 0, "items"],
                            "msg": "List should have at least 1 item after validation, not 0",
                            "input": [],
                            "ctx": {"field_type": "List", "min_length": 1, "actual_length": 0},
                        }
                    ]
                },
            ),
            # Empty item name
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "string_too_short",
                            "loc": ["body", "bills", 0, "items", 0, "name"],
                            "msg": "String should have at least 1 character",
                            "input": "",
                            "ctx": {"min_length": 1},
                        }
                    ]
                },
            ),
            # Zero price
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "greater_than",
                            "loc": ["body", "bills", 0, "items", 0, "price"],
                            "msg": "Input should be greater than 0",
                            "input": 0,
                            "ctx": {"gt": 0},
                        }
                    ]
                },
            ),
            # Negative price
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "greater_than",
                            "loc": ["body", "bills", 0, "items", 0, "price"],
                            "msg": "Input should be greater than 0",
                            "input": -100,
                            "ctx": {"gt": 0},
                        }
                    ]
                },
            ),
            # Zero quantity
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "greater_than",
                            "loc": ["body", "bills", 0, "items", 0, "quantity"],
                            "msg": "Input should be greater than 0",
                            "input": 0,
                            "ctx": {"gt": 0},
                        }
                    ]
                },
            ),
            # Negative quantity
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "greater_than",
                            "loc": ["body", "bills", 0, "items", 0, "quantity"],
                            "msg": "Input should be greater than 0",
                            "input": -5,
                            "ctx": {"gt": 0},
                        }
                    ]
                },
            ),
            # Empty consumed_by
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "too_short",
                            "loc": ["body", "bills", 0, "items", 0, "consumed_by"],
                            "msg": "List should have at least 1 item after validation, not 0",
                            "input": [],
                            "ctx": {"field_type": "List", "min_length": 1, "actual_length": 0},
                        }
                    ]
                },
            ),
            # Empty paid_by
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "string_too_short",
                            "loc": ["body", "bills", 0, "paid_by"],
                            "msg": "String should have at least 1 character",
                            "input": "",
                            "ctx": {"min_length": 1},
                        }
                    ]
                },
            ),
            # Negative tax rate
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "greater_than_equal",
                            "loc": ["body", "bills", 0, "tax_rate"],
                            "msg": "Input should be greater than or equal to 0",
                            "input": -0.05,
                            "ctx": {"ge": 0},
                        }
                    ]
                },
            ),
            # Tax rate greater than one
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "less_than_equal",
                            "loc": ["body", "bills", 0, "tax_rate"],
                            "msg": "Input should be less than or equal to 1",
                            "input": 1.5,
                            "ctx": {"le": 1},
                        }
                    ]
                },
            ),
            # Negative service charge
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "greater_than_equal",
                            "loc": ["body", "bills", 0, "service_charge"],
                            "msg": "Input should be greater than or equal to 0",
                            "input": -0.1,
                            "ctx": {"ge": 0},
                        }
                    ]
                },
            ),
            # Service charge greater than one
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "less_than_equal",
                            "loc": ["body", "bills", 0, "service_charge"],
                            "msg": "Input should be less than or equal to 1",
                            "input": 1.5,
                            "ctx": {"le": 1},
                        }
                    ]
                },
            ),
            # Missing bills field
            (
                {},
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills"],
                            "msg": "Field required",
                            "input": {},
                        }
                    ]
                },
            ),
            # Missing paid_by field
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills", 0, "paid_by"],
                            "msg": "Field required",
                            "input": {
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
                            },
                        }
                    ]
                },
            ),
            # Missing items field
            (
                {
                    "bills": [
                        {
                            "paid_by": "bob",
                            "tax_rate": 0.05,
                            "service_charge": 0.1,
                            "amount_paid": 1,
                        }
                    ]
                },
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills", 0, "items"],
                            "msg": "Field required",
                            "input": {
                                "paid_by": "bob",
                                "tax_rate": 0.05,
                                "service_charge": 0.1,
                                "amount_paid": 1,
                            },
                        }
                    ]
                },
            ),
            # Missing name field
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills", 0, "items", 0, "name"],
                            "msg": "Field required",
                            "input": {
                                "price": 600,
                                "quantity": 1,
                                "consumed_by": ["alice", "bob"],
                            },
                        }
                    ]
                },
            ),
            # Missing price field
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills", 0, "items", 0, "price"],
                            "msg": "Field required",
                            "input": {
                                "name": "Pizza",
                                "quantity": 1,
                                "consumed_by": ["alice", "bob"],
                            },
                        }
                    ]
                },
            ),
            # Missing quantity field
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills", 0, "items", 0, "quantity"],
                            "msg": "Field required",
                            "input": {
                                "name": "Pizza",
                                "price": 600,
                                "consumed_by": ["alice", "bob"],
                            },
                        }
                    ]
                },
            ),
            # Missing consumed_by field
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills", 0, "items", 0, "consumed_by"],
                            "msg": "Field required",
                            "input": {
                                "name": "Pizza",
                                "price": 600,
                                "quantity": 1,
                            },
                        }
                    ]
                },
            ),
            # Missing amount_paid field
            (
                {
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
                },
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "bills", 0, "amount_paid"],
                            "msg": "Field required",
                            "input": {
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
                            },
                        }
                    ]
                },
            ),
        ],
    )
    def test_input_validation_failure(self, test_client, outing_data: dict, error_response: dict):
        response = test_client.post("/api/v1/bills/split", json=outing_data)
        assert response.status_code == 422
        print(response.json())
        assert response.json() == error_response


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
