from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.schemas.bill import OCRBill, Outing, OutingSplit
from app.services.bill import OutingPaymentBalance
from tests import examples


class TestSplit:
    def mock_calculate_balance(self, monkeypatch: pytest.MonkeyPatch, mock_balance: OutingPaymentBalance):
        def mock(_: Outing):
            return mock_balance

        monkeypatch.setattr("app.api.v1.endpoints.bill.calculate_balance", mock)

    def mock_calculate_outing_split_with_minimal_transactions(
        self, monkeypatch: pytest.MonkeyPatch, mock_split: OutingSplit
    ):
        def mock(_: OutingPaymentBalance):
            return mock_split

        monkeypatch.setattr("app.api.v1.endpoints.bill.calculate_outing_split_with_minimal_transactions", mock)

    @pytest.mark.parametrize(
        "outing, balance, split",
        [
            (
                examples.simple_bill.OUTING,
                examples.simple_bill.OUTING_PAYMENT_BALANCE,
                examples.simple_bill.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
            (
                examples.multiple_bills.OUTING,
                examples.multiple_bills.OUTING_PAYMENT_BALANCE,
                examples.multiple_bills.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
            (
                examples.simple_bill_discounted.OUTING,
                examples.simple_bill_discounted.OUTING_PAYMENT_BALANCE,
                examples.simple_bill_discounted.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
            (
                examples.multiple_bills_discounted.OUTING,
                examples.multiple_bills_discounted.OUTING_PAYMENT_BALANCE,
                examples.multiple_bills_discounted.OUTING_SPLIT_WITH_MINIMAL_TRANSACTIONS,
            ),
        ],
    )
    def test_examples(
        self,
        monkeypatch: pytest.MonkeyPatch,
        test_client: TestClient,
        outing: Outing,
        balance: OutingPaymentBalance,
        split: OutingSplit,
    ):
        self.mock_calculate_balance(monkeypatch, balance)
        self.mock_calculate_outing_split_with_minimal_transactions(monkeypatch, split)

        response = test_client.post("/api/v1/bills/split", json=outing.model_dump())
        assert response.status_code == 200
        assert response.json() == split.model_dump()

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
    success_bill = examples.simple_bill.OCR_BILL

    @pytest.fixture
    def _mock_bill_service_method(self, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
        def mock_get_bill_details_from_image(image_bytes: bytes, mime_type: str) -> OCRBill:
            return self.success_bill

        monkeypatch.setattr("app.core.settings.settings.GEMINI_API_KEY", None)
        monkeypatch.setattr("app.api.v1.endpoints.bill.get_bill_details_from_image", mock_get_bill_details_from_image)
        yield None

    def test_valid_image_file(self, test_client, _mock_bill_service_method: None):
        files = {"file": ("test_image.png", b"dummy image content", "image/png")}
        response = test_client.post("/api/v1/bills/ocr", files=files)
        assert response.status_code == 200
        ocr_response = response.text
        assert OCRBill.model_validate_json(ocr_response) == self.success_bill

    @pytest.mark.parametrize(
        "files, status_code, error_response",
        [
            # Missing file
            (
                {},
                422,
                {"detail": [{"type": "missing", "loc": ["body", "file"], "msg": "Field required", "input": None}]},
            ),
            # Missing file
            (
                None,
                422,
                {"detail": [{"type": "missing", "loc": ["body", "file"], "msg": "Field required", "input": None}]},
            ),
            # Invalid file type
            (
                {"file": ("test.txt", b"dummy content", "text/plain")},
                400,
                {"detail": "Invalid file type. Please upload an image file."},
            ),
        ],
    )
    def test_input_validation_failure(self, test_client, files: dict | None, status_code: int, error_response: dict):
        response = test_client.post("/api/v1/bills/ocr", files=files)
        assert response.status_code == status_code
        print(response.json())
        assert response.json() == error_response
