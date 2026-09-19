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

def test_book_flight_success() -> None:
    """
    Verify that a flight is successfully booked with valid inputs.
    """
    destination = "Tokyo"
    date = "2026-11-15"
    time = "14:00"

    result = tools.book_flight.run({
        "destination": destination,
        "date": date,
        "time": time
    })

    assert "Flight Booking Confirmed" in result
    assert "Booking ID: FLT-2026-1024" in result
    assert "Destination: Tokyo" in result
    assert "Date: November 15, 2026" in result
    assert "Time: 2:00 PM" in result
    assert "Status: CONFIRMED" in result

def test_book_flight_validation() -> None:
    """
    Verify that validation errors are returned when required fields are missing.
    """
    # Missing destination
    res1 = tools.book_flight.run({
        "destination": "",
        "date": "2026-11-15",
        "time": "14:00"
    })
    assert "destination is empty" in res1

    # Missing date
    res2 = tools.book_flight.run({
        "destination": "Tokyo",
        "date": "",
        "time": "14:00"
    })
    assert "date is missing" in res2

    # Missing time
    res3 = tools.book_flight.run({
        "destination": "Tokyo",
        "date": "2026-11-15",
        "time": ""
    })
    assert "time is missing" in res3
