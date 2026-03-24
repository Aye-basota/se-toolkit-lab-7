"""
Slash command handlers.

Each handler is a pure function:
- Takes command arguments as input
- Returns a text response
- Has no Telegram dependencies

Handlers use the LMSClient service for backend API calls.
"""

from config import settings
from services import LMSClient


def _get_client() -> LMSClient:
    """Create an LMS client from settings."""
    return LMSClient(settings.lms_api_base_url, settings.lms_api_key)


def handle_start() -> str:
    """Handle /start command — welcome message."""
    return f"Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command — list available commands."""
    return """Available commands:
/start — Welcome message
/help — Show this help message
/health — Check backend status
/labs — List available labs
/scores <lab> — Show pass rates for a lab (e.g., /scores lab-04)

You can also ask questions in plain language:
- "what labs are available?"
- "show me scores for lab 4"
- "which lab has the lowest pass rate?" """


def handle_health() -> str:
    """Handle /health command — check backend status."""
    client = _get_client()
    is_healthy, message = client.health_check()
    return message


def handle_labs() -> str:
    """Handle /labs command — list available labs."""
    client = _get_client()
    success, result = client.get_items()

    if not success:
        return str(result)

    items = result
    if not items:
        return "No labs available. The backend may be empty."

    # Group items by lab - backend returns 'type', 'id', 'title' for labs
    labs = {}
    for item in items:
        if item.get("type") == "lab":
            lab_id = item.get("id", "unknown")
            lab_name = item.get("title", "Unknown Lab")
            # Generate a lab identifier like "lab-01" from the title
            if lab_id not in labs:
                labs[lab_id] = lab_name

    if not labs:
        return "No labs found in the backend."

    lines = ["Available labs:"]
    for lab_id, lab_name in sorted(labs.items()):
        lines.append(f"- {lab_name}")

    return "\n".join(lines)


def handle_scores(lab: str | None = None) -> str:
    """Handle /scores command — show pass rates for a lab.

    Args:
        lab: Lab identifier (e.g., 'lab-04')
    """
    if not lab:
        return "Please specify a lab, e.g., /scores lab-04"

    client = _get_client()
    success, result = client.get_pass_rates(lab)

    if not success:
        return str(result)

    pass_rates = result
    if not pass_rates:
        return f"No pass rate data found for {lab}."

    # Format pass rates - backend returns 'task', 'avg_score', 'attempts'
    lines = [f"Pass rates for {lab}:"]
    for task_data in pass_rates:
        task_name = task_data.get("task", "Unknown task")
        avg_score = task_data.get("avg_score", 0)
        attempts = task_data.get("attempts", 0)
        percentage = f"{avg_score:.1f}%" if isinstance(avg_score, (int, float)) else str(avg_score)
        lines.append(f"- {task_name}: {percentage} ({attempts} attempts)")

    return "\n".join(lines)
