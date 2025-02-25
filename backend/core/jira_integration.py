from jira import JIRA
from django.conf import settings
from typing import List, Optional, Dict, Any
from jira.exceptions import JIRAError
import logging
import functools
import time

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Decorator for retrying a function with exponential backoff.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise  # Re-raise the exception after the last attempt
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

def format_error_message(exception: Exception) -> Dict[str, str]:
    """
    Formats an exception into a user-friendly error message and a detailed error log.
    """
    error_message = str(exception)
    error_type = type(exception).__name__

    if isinstance(exception, JIRAError):
         # Handle JIRAError specifically
        status_code = exception.status_code
        error_details = exception.text
        formatted_message = (f"Jira Error ({status_code}): {error_message}.  Details: {error_details}")
    else:
        # Generic error handling
        formatted_message = f"{error_type}: {error_message}"

    # Prepare and return a dict
    error_info = {
        "error": formatted_message
    }

    logger.error(formatted_message)
    return error_info

class JiraClient:
    def __init__(self, server_url: str = None, user_email: str = None, api_token: str = None):
        """
        Initialize the Jira client.
        """
        try:
            self.server_url = server_url or settings.JIRA_SERVER_URL
            self.user_email = user_email or settings.JIRA_USER_EMAIL
            self.api_token = api_token or settings.JIRA_API_TOKEN

            logger.info("Initializing Jira client...")
            self.client = JIRA(
                server=self.server_url,
                basic_auth=(self.user_email, self.api_token)
            )
            logger.info("Jira client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jira client: {str(e)}")
            raise Exception(f"Failed to initialize Jira client: {str(e)}")
    @retry_with_backoff(max_retries=3)
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Fetches a single Jira issue by its key.
        """
        try:
            logger.info(f"Fetching issue {issue_key}")
            issue = self.client.issue(issue_key)

            return {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'description': issue.fields.description or '',
                'created': str(issue.fields.created),
                'priority': issue.fields.priority.name if issue.fields.priority else None,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                # Add any other fields you want to display
                'comments': [{
                    'author': comment.author.displayName,
                    'body': comment.body,
                    'created': str(comment.created)
                } for comment in issue.fields.comment.comments] if issue.fields.comment else []
            }

        except JIRAError as e:
            logger.error(f"Error fetching issue {issue_key}: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=3)
    def get_user_issues(self, jira_user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """
        Fetch issues assigned to a specific user, optionally filtered by status.
        """
        try:
            logger.info(f"Fetching issues for user {jira_user_id}")
            jql = f'assignee = {jira_user_id}'
            if status:
                jql += f' AND status = "{status}"'

            issues = self.client.search_issues(jql)
            logger.info(f"Found {len(issues)} issues for user {jira_user_id}")

            return [{
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'description': issue.fields.description or '',
                'created': str(issue.fields.created),
                'priority': issue.fields.priority.name if issue.fields.priority else None
            } for issue in issues]

        except JIRAError as e:
            logger.error(f"Error fetching user issues: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=3)
    def add_comment_to_issue(self, issue_key: str, comment: str, mentions: List[str] = None) -> Dict[str, Any]:
        """
        Add a comment to an issue, optionally mentioning users.
        """
        try:
            logger.info(f"Adding comment to issue {issue_key}")
            if mentions:
                formatted_mentions = ' '.join([f'[~{user_id}]' for user_id in mentions])
                comment = f"{formatted_mentions} {comment}"

            comment = self.client.add_comment(issue_key, comment)
            logger.info(f"Successfully added comment to issue {issue_key}")

            return {
                'id': comment.id,
                'body': comment.body,
                'author': comment.author.displayName,
                'created': str(comment.created)
            }

        except JIRAError as e:
            logger.error(f"Error adding comment to issue {issue_key}: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=3)
    def update_issue_status(self, issue_key: str, new_status: str) -> Dict[str, Any]:
        """
        Update the status of an issue.
        """
        try:
            logger.info(f"Updating status of issue {issue_key} to {new_status}")
            issue = self.client.issue(issue_key)
            transitions = self.client.transitions(issue)

            transition_id = None
            valid_transitions = []

            for t in transitions:
                valid_transitions.append(t['name'])
                if t['name'].lower() == new_status.lower():
                    transition_id = t['id']
                    break

            if not transition_id:
                error_msg = f"Invalid status '{new_status}'. Valid transitions are: {', '.join(valid_transitions)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            self.client.transition_issue(issue, transition_id)
            logger.info(f"Successfully updated issue {issue_key} status to {new_status}")

            updated_issue = self.client.issue(issue_key)
            return {
                'key': issue_key,
                'status': updated_issue.fields.status.name,
                'message': f"Successfully updated issue status to {new_status}"
            }

        except (JIRAError, ValueError) as e:
            logger.error(f"Error updating issue status: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=3)
    def create_issue(self, project_key: str, summary: str, description: str,
                     issue_type: str, assignee: str = None) -> Dict[str, Any]:
        """
        Create a new issue in Jira.
        """
        try:
            logger.info(f"Creating new issue in project {project_key}")
            if not all([project_key, summary, description, issue_type]):
                raise ValueError("All mandatory fields must be provided")

            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type}
            }

            if assignee:
                issue_dict['assignee'] = {'name': assignee}

            new_issue = self.client.create_issue(fields=issue_dict)
            logger.info(f"Successfully created issue {new_issue.key}")

            return {
                'key': new_issue.key,
                'summary': new_issue.fields.summary,
                'status': new_issue.fields.status.name,
                'assignee': new_issue.fields.assignee if new_issue.fields.assignee else None
            }

        except (JIRAError, ValueError) as e:
            logger.error(f"Error creating issue: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=3)
    def get_all_statuses(self) -> List[Dict[str, str]]:
        """
        Fetch all available statuses in Jira.
        """
        try:
            logger.info("Fetching all Jira statuses")
            statuses = self.client.statuses()
            logger.info(f"Successfully retrieved {len(statuses)} statuses")
            return [{
                'id': status.id,
                'name': status.name,
                'description': status.description
            } for status in statuses]

        except JIRAError as e:
            logger.error(f"Error fetching statuses: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=3)
    def search_users(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Search for users in Jira.  If query is empty, returns all users.
        """
        try:
            logger.info(f"Searching users with query: {query if query else 'all'}")
            search_query = query if query else '*'  # Use wildcard for empty query
            users = self.client.search_users(query=search_query, maxResults=50, includeActive=True, includeInactive=False)
            logger.info(f"Found {len(users)} users")

            return [{
                'account_id': user.accountId,
                'display_name': user.displayName,
                'email': getattr(user, 'emailAddress', None),  # Use getattr for optional attributes
                'active': user.active
            } for user in users]

        except JIRAError as e:
            logger.error(f"Error searching users: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])