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

def test_book_meeting_success() -> None:
    """
    Verify that a meeting is successfully booked with valid inputs.
    """
    participants = ["Alice", "Bob"]
    date = "2026-10-01"
    time = "10:00"

    result = tools.book_meeting.run({
        "participants": participants,
        "date": date,
        "time": time
    })

    assert "Meeting booked successfully" in result
    assert "Meeting ID: MTG-1024" in result
    assert "Alice, Bob" in result
    assert "October 01, 2026" in result
    assert "10:00 AM" in result

def test_book_meeting_validation() -> None:
    """
    Verify that validation errors are returned when required fields are missing.
    """
    # Missing participants
    res1 = tools.book_meeting.run({
        "participants": [],
        "date": "2026-10-01",
        "time": "10:00"
    })
    assert "participant list is empty" in res1

    # Missing date
    res2 = tools.book_meeting.run({
        "participants": ["Alice"],
        "date": "",
        "time": "10:00"
    })
    assert "date is missing" in res2

    # Missing time
    res3 = tools.book_meeting.run({
        "participants": ["Alice"],
        "date": "2026-10-01",
        "time": ""
    })
    assert "time is missing" in res3
