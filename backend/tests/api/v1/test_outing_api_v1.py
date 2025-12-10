from fastapi.testclient import TestClient

from app.main import app

test_client = TestClient(app)


def test_split__simple_bill_split_with_tax_and_service_charge():
    outing_data = {
        "bills": [
            {
                "paid_by": "Bob",
                "tax_rate": 0.05,
                "service_charge": 0.1,
                "items": [
                    {
                        "name": "Pizza",
                        "price": 600,
                        "quantity": 1,
                        "consumed_by": ["Alice", "Bob", "Charlie"],
                    },
                    {
                        "name": "Coke",
                        "price": 150,
                        "quantity": 1,
                        "consumed_by": ["Alice", "Bob"],
                    },
                    {
                        "name": "Ice Cream",
                        "price": 300,
                        "quantity": 1,
                        "consumed_by": ["Charlie"],
                    },
                ],
            }
        ]
    }

    response = test_client.post("/api/v1/outings/split", json=outing_data)
    assert response.status_code == 200

    outing_split = response.json()

    assert "payment_plans" in outing_split
    payment_plans = outing_split["payment_plans"]
    assert len(payment_plans) == 2

    for payment_plan in payment_plans:
        assert "name" in payment_plan
        assert payment_plan["name"] in ["Alice", "Charlie"]
        assert "payments" in payment_plan

        if payment_plan["name"] == "Alice":
            assert len(payment_plan["payments"]) == 1
            assert payment_plan["payments"][0]["to"] == "Bob"
            assert round(payment_plan["payments"][0]["amount"], 2) == 316.25
        elif payment_plan["name"] == "Charlie":
            assert len(payment_plan["payments"]) == 1
            assert payment_plan["payments"][0]["to"] == "Bob"
            assert round(payment_plan["payments"][0]["amount"], 2) == 575.00


def test_split__multiple_bills_with_different_service_charges_and_no_tax():
    outing_data = {
        "bills": [
            {
                "paid_by": "Alice",
                "tax_rate": 0,
                "service_charge": 0.1,
                "items": [
                    {
                        "name": "Pizza",
                        "price": 900,
                        "quantity": 1,
                        "consumed_by": ["Alice", "Bob", "Charlie"],
                    }
                ],
            },
            {
                "paid_by": "Bob",
                "tax_rate": 0,
                "service_charge": 0.15,
                "items": [
                    {
                        "name": "Coffee",
                        "price": 300,
                        "quantity": 1,
                        "consumed_by": ["Alice", "Charlie"],
                    },
                    {
                        "name": "Cake",
                        "price": 450,
                        "quantity": 1,
                        "consumed_by": ["Alice", "Bob", "Charlie"],
                    },
                ],
            },
        ]
    }

    response = test_client.post("/api/v1/outings/split", json=outing_data)
    assert response.status_code == 200

    outing_split = response.json()

    assert "payment_plans" in outing_split
    payment_plans = outing_split["payment_plans"]
    assert len(payment_plans) == 1

    payment_plan = payment_plans[0]
    assert "name" in payment_plan
    assert payment_plan["name"] == "Charlie"

    assert "payments" in payment_plan
    for payment in payment_plan["payments"]:
        assert "to" in payment
        assert payment["to"] in ["Bob", "Alice"]
        assert "amount" in payment
        if payment["to"] == "Alice":
            assert round(payment["amount"], 2) == 315.00
        elif payment["to"] == "Bob":
            assert round(payment["amount"], 2) == 360.00
