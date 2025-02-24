from jira import JIRA
from django.conf import settings
from typing import List, Optional, Dict, Any
from jira.exceptions import JIRAError
import logging
from .api_utils import retry_with_backoff, format_error_message

# Configure logging
logger = logging.getLogger(__name__)

class JiraClient:
    def __init__(self, server_url: str = None, user_email: str = None, api_token: str = None):
        """
        Initialize the Jira client with authentication credentials.
        If not provided, credentials will be loaded from environment variables.
        """
        try:
            self.server_url = server_url or settings.JIRA_SERVER_URL
            self.user_email = user_email or settings.JIRA_USER_EMAIL
            self.api_token = api_token or settings.JIRA_API_TOKEN

            # Validate URL format
            if not self.server_url.startswith(('http://', 'https://')):
                self.server_url = f'https://{self.server_url}'  # Default to HTTPS
                logger.warning(f"Auto-corrected server URL to include scheme: {self.server_url}")


            logger.info("Initializing Jira client...")
            # Initialize Jira client
            self.client = JIRA(
                server=self.server_url,
                basic_auth=(self.user_email, self.api_token)
            )
            logger.info("Jira client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jira client: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=3)
    def get_user_issues(self, jira_user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """
        Fetch issues assigned to a specific user, optionally filtered by status.
        """
        try:
            logger.info(f"Fetching issues for user {jira_user_id}")
            # Construct JQL query
            jql = f'assignee = {jira_user_id}'
            if status:
                jql += f' AND status = "{status}"'

            # Execute JQL query
            issues = self.client.search_issues(jql)
            logger.info(f"Found {len(issues)} issues for user {jira_user_id}")

            # Format response
            return [{
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'description': issue.fields.description or '',
                'created': str(issue.fields.created),
                'updated': str(issue.fields.updated),
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
            # Format mentions if provided
            if mentions:
                formatted_mentions = ' '.join([f'[~{user_id}]' for user_id in mentions])
                comment = f"{formatted_mentions} {comment}"

            # Add comment
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
            
            # Find the transition ID for the new status
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

            # Perform the transition
            self.client.transition_issue(issue, transition_id)
            logger.info(f"Successfully updated issue {issue_key} status to {new_status}")
            
            # Refresh issue data
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
            # Validate mandatory fields
            if not all([project_key, summary, description, issue_type]):
                raise ValueError("All mandatory fields must be provided")

            # Prepare issue fields
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type}
            }

            if assignee:
                issue_dict['assignee'] = {'name': assignee}

            # Create the issue
            new_issue = self.client.create_issue(fields=issue_dict)
            logger.info(f"Successfully created issue {new_issue.key}")
            
            return {
                'key': new_issue.key,
                'summary': new_issue.fields.summary,
                'status': new_issue.fields.status.name,
                'assignee': new_issue.fields.assignee.displayName if new_issue.fields.assignee else None
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
        Search for users in Jira. If query is empty, returns all users.
        """
        try:
            logger.info(f"Searching users with query: {query if query else 'all'}")
            # If query is None or empty, use a wildcard search
            search_query = query if query else ''
            users = self.client.search_users(query=search_query)
            logger.info(f"Found {len(users)} users")

            return [{
                'account_id': user.accountId,
                'display_name': user.displayName,
                'email': getattr(user, 'emailAddress', None),
                'active': user.active
            } for user in users]

        except JIRAError as e:
            logger.error(f"Error searching users: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])