import pytest
from pathlib import Path
from toolcalling_proj.tools_manager import tools

@pytest.fixture(autouse=True)
def setup_test_data(monkeypatch, tmp_path):
    """
    Fixture to isolate tool data for each test.
    Monkeypatches the DATA_DIR and all CSV file paths in the tools module
    to use a temporary directory provided by pytest.
    """
    test_data_dir = tmp_path / "data"
    test_data_dir.mkdir()

    # Patch the main DATA_DIR
    monkeypatch.setattr(tools, "DATA_DIR", test_data_dir)

    # Patch individual file paths since they are evaluated at module load time
    monkeypatch.setattr(tools, "TODO_FILE", test_data_dir / "todo.csv")
    monkeypatch.setattr(tools, "MEETINGS_FILE", test_data_dir / "meetings.csv")
    monkeypatch.setattr(tools, "FLIGHTS_FILE", test_data_dir / "flight_bookings.csv")
    monkeypatch.setattr(tools, "ORDERS_FILE", test_data_dir / "orders.csv")

def test_place_order_success() -> None:
    """
    Verify that an order is placed successfully with a valid list of items.
    """
    items = [
        {"name": "mechanical keyboard", "quantity": 1},
        {"name": "usb-c cable", "quantity": 3},
    ]

    result = tools.place_order.run({
        "items": items
    })

    assert "Order Placed Successfully" in result
    assert "Order ID: ORD-10482" in result
    assert "- Mechanical Keyboard x 1" in result
    assert "- Usb-C Cable x 3" in result
    assert "Status: CONFIRMED" in result

def test_place_order_validation_empty() -> None:
    """
    Verify that an order cannot be placed with an empty item list.
    """
    result = tools.place_order.run({
        "items": []
    })
    assert "no items were provided" in result

def test_place_order_validation_invalid_item() -> None:
    """
    Verify that an order cannot be placed if an item is not a dictionary.
    """
    items = ["not a dict"]
    result = tools.place_order.func(items)
    assert "item is not a valid object" in result

def test_place_order_validation_missing_name() -> None:
    """
    Verify that an order cannot be placed if an item is missing a name.
    """
    items = [{"quantity": 1}]
    result = tools.place_order.run({
        "items": items
    })
    assert "item is missing a name" in result

def test_place_order_validation_invalid_quantity() -> None:
    """
    Verify that an order cannot be placed if quantity is invalid or non-positive.
    """
    # Non-integer quantity
    items_bad_type = [{"name": "pen", "quantity": "abc"}]
    res1 = tools.place_order.run({"items": items_bad_type})
    assert "quantity for \"pen\" is invalid" in res1

    # Zero quantity
    items_zero = [{"name": "pen", "quantity": 0}]
    res2 = tools.place_order.run({"items": items_zero})
    assert "quantity for \"pen\" must be greater than zero" in res2

    # Negative quantity
    items_neg = [{"name": "pen", "quantity": -5}]
    res3 = tools.place_order.run({"items": items_neg})
    assert "quantity for \"pen\" must be greater than zero" in res3
