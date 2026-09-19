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

def test_add_task_success() -> None:
    """
    Verify that a task is successfully added to the todo list.
    """
    task_name = "Finish Smoke Tests"
    result = tools.add_task.run({"task_name": task_name})

    assert f'Task added successfully: "{task_name}"' in result
    assert "status: pending" in result

def test_update_task_status_success() -> None:
    """
    Verify that a task status can be updated correctly.
    """
    task_name = "Update Me"
    tools.add_task.run({"task_name": task_name})

    result = tools.update_task_status.run({
        "task_name": task_name,
        "status": "completed"
    })

    assert f'Task updated: "{task_name}" -> completed' in result

def test_update_task_status_invalid() -> None:
    """
    Verify that an invalid status update is rejected.
    """
    task_name = "Invalid Status Test"
    tools.add_task.run({"task_name": task_name})

    result = tools.update_task_status.run({
        "task_name": task_name,
        "status": "done"
    }) # Not in ALLOWED_TASK_STATUSES
    assert "Invalid status" in result

def test_list_tasks_all() -> None:
    """
    Verify that all added tasks are listed when no status filter is provided.
    """
    tools.add_task.run({"task_name": "Task 1"})
    tools.add_task.run({"task_name": "Task 2"})

    result = tools.list_tasks.run({})

    assert "Your tasks:" in result
    assert "Task 1 [pending]" in result
    assert "Task 2 [pending]" in result

def test_list_tasks_filtered() -> None:
    """
    Verify that listing tasks with a specific status filter works correctly.
    """
    tools.add_task.run({"task_name": "Pending Task"})
    tools.add_task.run({"task_name": "Completed Task"})
    tools.update_task_status.run({
        "task_name": "Completed Task",
        "status": "completed"
    })

    # Filter by completed
    res_completed = tools.list_tasks.run({"status": "completed"})
    assert 'Your "completed" tasks:' in res_completed
    assert "Completed Task [completed]" in res_completed
    assert "Pending Task" not in res_completed

    # Filter by pending
    res_pending = tools.list_tasks.run({"status": "pending"})
    assert 'Your "pending" tasks:' in res_pending
    assert "Pending Task [pending]" in res_pending
    assert "Completed Task" not in res_pending
