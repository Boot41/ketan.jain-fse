"""
Utility functions for the core app.
"""
import re
from typing import Optional, Tuple, List
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ScrumUpdate
from .jira_integration import JiraClient, JiraClientError

def get_scrum_update(user: User, date=None) -> Optional[ScrumUpdate]:
    """
    Check if a scrum update exists for the given user and date.
    
    Args:
        user: The user to check for
        date: Optional date to check for. If not provided, uses today's date.
        
    Returns:
        ScrumUpdate object if found, None otherwise
    """
    if date is None:
        date = timezone.now().date()
    try:
        return ScrumUpdate.objects.get(user=user, date=date)
    except ScrumUpdate.DoesNotExist:
        return None


def create_scrum_update(user: User, updates: str, jira_client: JiraClient) -> Tuple[ScrumUpdate, List[str]]:
    """
    Create a new scrum update and tag any mentioned Jira issues.
    
    Args:
        user: The user creating the update
        updates: The text content of the scrum update
        jira_client: An initialized JiraClient instance
        
    Returns:
        Tuple containing:
        - The created ScrumUpdate object
        - List of strings describing the results of tagging Jira issues
    """
    date = timezone.now().date()
    
    # Check if an update already exists for today
    existing_update = get_scrum_update(user, date)
    if existing_update:
        raise ValueError(f"Scrum update already exists for {date}")
    
    # Create the scrum update
    scrum_update = ScrumUpdate.objects.create(
        user=user,
        date=date,
        updates=updates
    )
    
    # Parse updates to find Jira issue keys (assuming format PROJECT-123)
    issue_keys = re.findall(r'[A-Z]+-\d+', updates)
    
    # Add comments to each mentioned Jira issue
    results = []
    for issue_key in set(issue_keys):  # Use set to avoid duplicate comments
        try:
            jira_client.add_comment_to_issue(
                issue_key=issue_key,
                comment=f"Daily Scrum Update from {user.get_full_name() or user.username}:\n{updates}"
            )
            results.append(f"Added scrum update to {issue_key}")
        except JiraClientError as e:
            results.append(f"Failed to add comment to {issue_key}: {str(e)}")
    
    return scrum_update, results


def format_scrum_update(yesterday: str, today: str, blockers: str) -> str:
    """
    Format the three parts of a scrum update into a single string.
    
    Args:
        yesterday: What was done yesterday
        today: What will be done today
        blockers: Any blockers or impediments
        
    Returns:
        Formatted string containing all parts of the scrum update
    """
    return (
        f"Yesterday: {yesterday}\n\n"
        f"Today: {today}\n\n"
        f"Blockers: {blockers}"
    )
