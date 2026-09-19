"""
Deterministic Python tools used by the AI personal assistant.

Important teaching point:
- The LLM decides WHICH tool to call and WHAT arguments to pass.
- These Python functions contain the real business logic and update local CSV files.

No external APIs. Everything is simulated with local files under data/.
"""

import csv
import json
import os
from pathlib import Path
from datetime import datetime

from langchain_core.tools import tool


# Absolute path to the project root (one level above src/).
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

TODO_FILE = DATA_DIR / "todo.csv"
MEETINGS_FILE = DATA_DIR / "meetings.csv"
FLIGHTS_FILE = DATA_DIR / "flight_bookings.csv"
ORDERS_FILE = DATA_DIR / "orders.csv"

ALLOWED_TASK_STATUSES = {"pending", "in_progress", "completed"}


def _next_id(prefix, number):
    """
    Build a simple readable ID like MTG-1024 or FLT-2026-1024.

    Args:
        prefix (str): Short prefix for the ID.
        number (int): Numeric part of the ID.

    Returns:
        str: Formatted ID string.
    """
    return f"{prefix}-{number}"


def _count_data_rows(file_path):
    """
    Count existing data rows in a CSV (excluding the header).

    Args:
        file_path (str): Path to a CSV file.

    Returns:
        int: Number of data rows currently stored.
    """
    if not os.path.exists(file_path):
        return 0

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)

    # First row is the header when the file is not empty.
    if len(rows) <= 1:
        return 0
    return len(rows) - 1


def _format_display_date(date_text):
    """
    Try to turn a date string into a friendly display format.

    Args:
        date_text (str): Date as provided by the LLM (e.g. 2026-09-15).

    Returns:
        str: A readable date when possible, otherwise the original text.
    """
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(date_text.strip(), fmt)
            return parsed.strftime("%B %d, %Y")
        except ValueError:
            continue
    return date_text


def _format_display_time(time_text):
    """
    Try to turn a time string into a friendly 12-hour display format.

    Args:
        time_text (str): Time as provided by the LLM (e.g. 15:00 or 3 PM).

    Returns:
        str: A readable time when possible, otherwise the original text.
    """
    cleaned = time_text.strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I %p", "%I:%M%p", "%I%p"):
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            continue
    return time_text


# ---------------------------------------------------------------------------
# Tool 1 — Meeting Booking
# ---------------------------------------------------------------------------


@tool
def book_meeting(participants: list[str], date: str, time: str) -> str:
    """
    Book a meeting and save it to data/meetings.csv.

    Use this tool only when participants, date, and time are all known.
    If any required value is missing, ask the user first — do not guess.

    Args:
        participants (list[str]): One or more people attending the meeting.
        date (str): Meeting date (for example: 2026-09-15 or September 15, 2026).
        time (str): Meeting time (for example: 15:00 or 3 PM).

    Returns:
        str: Confirmation text or a clear validation error.

    Example:
        result = book_meeting(
            participants=["Rahul"],
            date="2026-09-15",
            time="15:00",
        )
        print(result)
    """
    # Simple validation — return clear errors instead of inventing values.
    if not participants:
        return "Meeting could not be booked because the participant list is empty."

    cleaned_participants = [p.strip() for p in participants if str(p).strip()]
    if not cleaned_participants:
        return "Meeting could not be booked because the participant list is empty."

    if not date or not str(date).strip():
        return "Meeting could not be booked because the date is missing."

    if not time or not str(time).strip():
        return "Meeting could not be booked because the time is missing."

    last_meeting_number = 1024 + _count_data_rows(MEETINGS_FILE)
    meeting_id = _next_id("MTG", last_meeting_number)
    participants_text = ", ".join(cleaned_participants)
    display_date = _format_display_date(str(date))
    display_time = _format_display_time(str(time))
    status = "CONFIRMED"

    # Append the booking to the local CSV file.
    file_exists = os.path.exists(MEETINGS_FILE)

    MEETINGS_FILE.parent.mkdir(parents=True, exist_ok=True) # Ensure directory is present

    if not MEETINGS_FILE.exists():
        MEETINGS_FILE.touch() # Makes empty csv file

    with open(MEETINGS_FILE, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(MEETINGS_FILE) == 0: # For adding header cols if it is fresh empty csv file
            writer.writerow(["meeting_id", "participants", "date", "time", "status"])
        writer.writerow([meeting_id, participants_text, display_date, display_time, status])

    return (
        "Meeting booked successfully.\n\n"
        f"Meeting ID: {meeting_id}\n"
        f"Participants: {participants_text}\n"
        f"Date: {display_date}\n"
        f"Time: {display_time}\n"
        f"Status: {status}"
    )


# ---------------------------------------------------------------------------
# Tool 2 — Todo / Task Tracker
# ---------------------------------------------------------------------------


@tool
def add_task(task_name: str) -> str:
    """
    Add a new task to the local todo CSV file.

    Args:
        task_name (str): Name of the task to add.

    Returns:
        str: Confirmation message.

    Example:
        result = add_task("Prepare LangChain lecture")
        print(result)
    """
    if not task_name or not str(task_name).strip():
        return "Task could not be added because the task name is empty."

    cleaned_name = str(task_name).strip()

    file_exists = os.path.exists(TODO_FILE)
    with open(TODO_FILE, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(TODO_FILE) == 0:
            writer.writerow(["task_name", "status"])
        writer.writerow([cleaned_name, "pending"])

    return f'Task added successfully: "{cleaned_name}" (status: pending)'


@tool
def update_task_status(task_name: str, status: str) -> str:
    """
    Update the status of an existing task in data/todo.csv.

    Allowed statuses: pending, in_progress, completed.

    Args:
        task_name (str): Exact or close name of the task to update.
        status (str): New status value.

    Returns:
        str: Confirmation message or a clear error if the task is missing.

    Example:
        result = update_task_status(
            task_name="Prepare tool calling lecture",
            status="completed",
        )
        print(result)
    """
    if not task_name or not str(task_name).strip():
        return "Task could not be updated because the task name is empty."

    cleaned_status = str(status).strip().lower()
    if cleaned_status not in ALLOWED_TASK_STATUSES:
        return (
            f'Invalid status: "{status}". '
            "Allowed values are: pending, in_progress, completed."
        )

    if not os.path.exists(TODO_FILE):
        return f'Task not found: "{task_name}"'

    with open(TODO_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames or ["task_name", "status"]

    target = str(task_name).strip().lower()
    updated = False
    matched_name = None

    for row in rows:
        current_name = row.get("task_name", "").strip()
        # Match exact name, or allow a simple case-insensitive contains match.
        if current_name.lower() == target or target in current_name.lower():
            row["status"] = cleaned_status
            matched_name = current_name
            updated = True
            break

    if not updated:
        return f'Task not found: "{task_name}"'

    with open(TODO_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return f'Task updated: "{matched_name}" -> {cleaned_status}'


@tool
def list_tasks(status: str = "") -> str:
    """
    List tasks from data/todo.csv.

    If status is provided, only tasks with that status are returned.
    If status is empty, all tasks are returned.

    Args:
        status (str, optional): Filter by pending, in_progress, or completed.
            Leave empty to list every task.

    Returns:
        str: A readable task list, or a message if nothing matches.

    Example:
        print(list_tasks(status="pending"))
        print(list_tasks())
    """
    if not os.path.exists(TODO_FILE):
        return "No tasks found. Your todo list is empty."

    with open(TODO_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        return "No tasks found. Your todo list is empty."

    cleaned_status = str(status).strip().lower() if status else ""
    if cleaned_status:
        if cleaned_status not in ALLOWED_TASK_STATUSES:
            return (
                f'Invalid status filter: "{status}". '
                "Allowed values are: pending, in_progress, completed."
            )
        rows = [row for row in rows if row.get("status", "").strip().lower() == cleaned_status]

    if not rows:
        if cleaned_status:
            return f'No tasks found with status "{cleaned_status}".'
        return "No tasks found. Your todo list is empty."

    lines = []
    for index, row in enumerate(rows, start=1):
        name = row.get("task_name", "").strip()
        task_status = row.get("status", "").strip()
        lines.append(f"{index}. {name} [{task_status}]")

    header = "Your tasks:" if not cleaned_status else f'Your "{cleaned_status}" tasks:'
    return header + "\n" + "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 3 — Flight Booking
# ---------------------------------------------------------------------------


@tool
def book_flight(destination: str, date: str, time: str) -> str:
    """
    Book a simulated flight and save it to data/flight_bookings.csv.

    Use this tool only when destination, date, and time are all known.
    If any required value is missing, ask the user first — do not guess.

    Args:
        destination (str): Travel destination city (for example: Delhi).
        date (str): Travel date (for example: 2026-09-15).
        time (str): Departure time (for example: 10:00 or 10 AM).

    Returns:
        str: Confirmation text or a clear validation error.

    Example:
        result = book_flight(
            destination="Delhi",
            date="2026-09-15",
            time="10:00",
        )
        print(result)
    """
    if not destination or not str(destination).strip():
        return "Flight could not be booked because the destination is empty."

    if not date or not str(date).strip():
        return "Flight could not be booked because the date is missing."

    if not time or not str(time).strip():
        return "Flight could not be booked because the time is missing."

    booking_number = 1024 + _count_data_rows(FLIGHTS_FILE)
    booking_id = f"FLT-2026-{booking_number}"
    cleaned_destination = str(destination).strip()
    display_date = _format_display_date(str(date))
    display_time = _format_display_time(str(time))
    status = "CONFIRMED"

    file_exists = os.path.exists(FLIGHTS_FILE)
    with open(FLIGHTS_FILE, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(FLIGHTS_FILE) == 0:
            writer.writerow(["booking_id", "destination", "date", "time", "status"])
        writer.writerow([booking_id, cleaned_destination, display_date, display_time, status])

    return (
        "Flight Booking Confirmed\n\n"
        f"Booking ID: {booking_id}\n"
        f"Destination: {cleaned_destination}\n"
        f"Date: {display_date}\n"
        f"Time: {display_time}\n"
        f"Status: {status}"
    )


# ---------------------------------------------------------------------------
# Tool 4 — Shopping / Order Placement
# ---------------------------------------------------------------------------


@tool
def place_order(items: list[dict]) -> str:
    """
    Place a simulated shopping order and save it to data/orders.csv.

    Each item must include:
        - name (str)
        - quantity (int greater than 0)

    Args:
        items (list[dict]): List of items to order.
            Example: [{"name": "notebook", "quantity": 2}]

    Returns:
        str: Confirmation text or a clear validation error.

    Example:
        result = place_order(
            items=[
                {"name": "notebook", "quantity": 2},
                {"name": "blue pens", "quantity": 1},
                {"name": "laptop sleeve", "quantity": 1},
            ]
        )
        print(result)
    """
    if not items:
        return "Order could not be placed because no items were provided."

    cleaned_items = []
    for item in items:
        if not isinstance(item, dict):
            return "Order could not be placed because an item is not a valid object."

        name = str(item.get("name", "")).strip()
        quantity = item.get("quantity", 0)

        if not name:
            return "Order could not be placed because an item is missing a name."

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return f'Order could not be placed because quantity for "{name}" is invalid.'

        if quantity <= 0:
            return f'Order could not be placed because quantity for "{name}" must be greater than zero.'

        cleaned_items.append({"name": name, "quantity": quantity})

    order_number = 10482 + _count_data_rows(ORDERS_FILE)
    order_id = _next_id("ORD", order_number)
    status = "CONFIRMED"

    # Store items as a compact JSON string in the CSV for simplicity.
    items_json = json.dumps(cleaned_items)

    file_exists = os.path.exists(ORDERS_FILE)
    with open(ORDERS_FILE, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(ORDERS_FILE) == 0:
            writer.writerow(["order_id", "items", "status"])
        writer.writerow([order_id, items_json, status])

    item_lines = []
    for item in cleaned_items:
        pretty_name = item["name"].title()
        item_lines.append(f"- {pretty_name} x {item['quantity']}")

    return (
        "Order Placed Successfully\n\n"
        f"Order ID: {order_id}\n\n"
        "Items:\n"
        + "\n".join(item_lines)
        + f"\n\nStatus: {status}"
    )


def get_all_tools():
    """
    Return the list of LangChain tools available to the assistant.

    Returns:
        list: All @tool-decorated functions used by the LLM.

    Example:
        tools = get_all_tools()
        llm_with_tools = llm.bind_tools(tools)
    """
    return [
        book_meeting,
        add_task,
        update_task_status,
        list_tasks,
        book_flight,
        place_order,
    ]
