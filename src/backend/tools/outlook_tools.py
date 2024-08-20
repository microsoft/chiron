
from datetime import datetime
from langchain_core.tools import tool

@tool
def send_email(message: str, recipients: list[str]) -> str: # I wonder how well other return types might work
    """Send an email to a list of recipients."""
    # todo: add email sending logic
    return f"Sent email: {message} to {', '.join(recipients)}"

@tool
def create_calendar_event(event_name: str, datetime: datetime) -> str:
    """Create a calendar event in Outlook."""
    # todo: add event creation logic
    return f"Created an Outlook on {datetime} event named {event_name}"

__all__ = [send_email, create_calendar_event]