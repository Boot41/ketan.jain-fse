"""
Jira Integration Module

This module provides a client for interacting with the Jira API.
It handles all Jira-related operations including fetching issues,
managing comments, updating statuses, and creating new issues.
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any, Union
from requests.exceptions import RequestException
from jira import JIRA
from jira.exceptions import JIRAError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.cache import cache

# Configure logging
logger = logging.getLogger(__name__)

class JiraClientError(Exception):
    """Custom exception for Jira client errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class JiraConnectionError(JiraClientError):
    """Exception for connection-related errors"""
    pass

class JiraAuthenticationError(JiraClientError):
    """Exception for authentication-related errors"""
    pass

class JiraClient:
    """
    A client for interacting with the Jira API.
    
    This class provides methods for common Jira operations and handles
    authentication and error management with retries and caching.
    """
    
    # Class-level constants
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    CACHE_TTL = 300  # 5 minutes
    
    def __init__(self, server_url: Optional[str] = None, 
                 user_email: Optional[str] = None, 
                 api_token: Optional[str] = None,
                 max_retries: Optional[int] = None,
                 retry_delay: Optional[int] = None):
        """
        Initialize the Jira client with authentication credentials.
        
        Args:
            server_url: Jira server URL. If not provided, uses JIRA_SERVER_URL from env.
            user_email: Jira user email. If not provided, uses JIRA_USER_EMAIL from env.
            api_token: Jira API token. If not provided, uses JIRA_API_TOKEN from env.
            max_retries: Maximum number of retry attempts for failed requests.
            retry_delay: Delay between retry attempts in seconds.
            
        Raises:
            JiraAuthenticationError: If authentication fails.
            JiraConnectionError: If connection to Jira server fails.
            JiraClientError: For other initialization errors.
        """
        self.max_retries = max_retries or self.MAX_RETRIES
        self.retry_delay = retry_delay or self.RETRY_DELAY
        
        try:
            # Get credentials from parameters or environment
            self.server_url = server_url or os.getenv('JIRA_SERVER_URL')
            self.user_email = user_email or os.getenv('JIRA_USER_EMAIL')
            self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
            
            if not all([self.server_url, self.user_email, self.api_token]):
                raise JiraAuthenticationError(
                    "Missing required Jira credentials. Please check environment variables."
                )
            
            # Initialize the Jira client with retries
            self._initialize_client()
            
        except JIRAError as e:
            if e.status_code == 401:
                raise JiraAuthenticationError("Invalid credentials", status_code=401)
            elif e.status_code == 404:
                raise JiraConnectionError(f"Invalid Jira server URL: {self.server_url}", status_code=404)
            else:
                raise JiraClientError(f"JIRA API Error: {str(e)}", status_code=e.status_code)
        except RequestException as e:
            raise JiraConnectionError(f"Connection error: {str(e)}")
        except Exception as e:
            raise JiraClientError(f"Unexpected error: {str(e)}")
    
    def _initialize_client(self) -> None:
        """
        Initialize the Jira client with retry logic.
        
        Raises:
            JiraClientError: If all retry attempts fail.
        """
        for attempt in range(self.max_retries):
            try:
                options = {
                    'server': self.server_url,
                    'verify': True,  # Enable SSL verification
                    'timeout': 30,   # Set request timeout
                }
                
                self.client = JIRA(
                    options,
                    basic_auth=(self.user_email, self.api_token),
                    max_retries=2    # Additional request-level retries
                )
                
                # Test connection and cache user information
                user_info = self.client.myself()
                
                # Only cache if not in testing mode (to avoid caching MagicMock objects)
                if not settings.TESTING:
                    cache.set(f'jira_user_info_{self.user_email}', user_info, self.CACHE_TTL)
                    
                logger.info(f"Successfully connected to Jira as {user_info.displayName}")
                return
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise JiraClientError("Failed to initialize Jira client after all retry attempts")
    
    def _validate_issue_key(self, issue_key: str) -> None:
        """
        Validate the format of a Jira issue key.
        
        Args:
            issue_key: The issue key to validate (e.g., 'PROJECT-123')
            
        Raises:
            ValidationError: If the issue key format is invalid
        """
        if not issue_key or '-' not in issue_key:
            raise ValidationError(f"Invalid issue key format: {issue_key}")
        
        project_key, issue_number = issue_key.split('-')
        if not project_key.isalnum() or not issue_number.isdigit():
            raise ValidationError(f"Invalid issue key format: {issue_key}")
            
    def _build_jql_query(self, jira_user_id: str, status: Optional[str] = None) -> str:
        """
        Build a JQL query for fetching user issues.
        
        Args:
            jira_user_id: The Jira user ID to fetch issues for
            status: Optional status to filter issues by
            
        Returns:
            str: The constructed JQL query
        """
        query = f'assignee = "{jira_user_id}"'
        
        if status:
            # Cache valid statuses to avoid repeated API calls
            cache_key = 'jira_valid_statuses'
            valid_statuses = cache.get(cache_key)
            
            if not valid_statuses:
                valid_statuses = [s.name for s in self.client.statuses()]
                cache.set(cache_key, valid_statuses, self.CACHE_TTL)
            
            if status.upper() not in (s.upper() for s in valid_statuses):
                raise ValidationError(f"Invalid status: {status}. Valid statuses are: {', '.join(valid_statuses)}")
            
            query += f' AND status = "{status}"'
        
        query += ' ORDER BY updated DESC'
        return query
    
    def _format_issue(self, issue) -> Dict[str, Any]:
        """
        Format a Jira issue object into a dictionary with relevant information.
        
        Args:
            issue: Jira issue object
            
        Returns:
            Dict containing formatted issue data
        """
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'status': issue.fields.status.name,
            'description': issue.fields.description or '',
            'created': issue.fields.created,
            'updated': issue.fields.updated,
            'priority': issue.fields.priority.name if issue.fields.priority else None,
            'assignee': {
                'name': issue.fields.assignee.displayName,
                'email': issue.fields.assignee.emailAddress,
                'avatar': issue.fields.assignee.avatarUrls['48x48']
            } if issue.fields.assignee else None,
            'reporter': {
                'name': issue.fields.reporter.displayName,
                'email': issue.fields.reporter.emailAddress,
                'avatar': issue.fields.reporter.avatarUrls['48x48']
            } if issue.fields.reporter else None,
            'labels': issue.fields.labels,
            'components': [c.name for c in issue.fields.components],
            'url': f"{self.server_url}/browse/{issue.key}"
        }
    
    def get_user_issues(self, jira_user_id: str, status: Optional[str] = None,
                       max_results: int = 50, expand: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetch issues assigned to a specific user with optional status filter.
        
        Args:
            jira_user_id: The Jira user ID to fetch issues for
            status: Optional status to filter issues by (e.g., 'In Progress', 'Done')
            max_results: Maximum number of issues to return (default: 50)
            expand: List of fields to expand in the response
            
        Returns:
            List of dictionaries containing issue information
            
        Raises:
            JiraClientError: If there's an error fetching the issues
            ValidationError: If the status is invalid
        """
        try:
            # Build JQL query
            jql_query = self._build_jql_query(jira_user_id, status)
            logger.debug(f"Executing JQL query: {jql_query}")
            
            # Cache key for this specific query
            cache_key = f'jira_issues_{jira_user_id}_{status}_{max_results}'
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.debug("Returning cached issues")
                return cached_result
            
            # Fetch issues with pagination
            issues = []
            start_at = 0
            
            while len(issues) < max_results:
                batch = self.client.search_issues(
                    jql_query,
                    startAt=start_at,
                    maxResults=min(50, max_results - len(issues)),  # Jira's max batch size is 50
                    expand=expand or []
                )
                
                if not batch.issues:
                    break
                
                issues.extend(batch.issues)
                if len(batch.issues) < 50:
                    break
                    
                start_at += 50
            
            # Format and cache results
            formatted_issues = [self._format_issue(issue) for issue in issues[:max_results]]
            cache.set(cache_key, formatted_issues, 60)  # Cache for 1 minute
            
            return formatted_issues
            
        except JIRAError as e:
            if e.status_code == 400:
                raise ValidationError(f"Invalid JQL query: {str(e)}")
            raise JiraClientError(f"Error fetching issues: {str(e)}", status_code=e.status_code)
        except Exception as e:
            raise JiraClientError(f"Unexpected error fetching issues: {str(e)}")
            
    def _format_mentions(self, comment: str, mentions: Optional[List[str]] = None) -> str:
        """
        Format a comment to include @mentions in Jira's format.
        
        Args:
            comment: The comment text
            mentions: List of Jira user IDs to mention
            
        Returns:
            Formatted comment string with mentions
        """
        if not mentions:
            return comment
            
        # Cache user info to avoid repeated API calls
        user_info = {}
        for user_id in mentions:
            cache_key = f'jira_user_{user_id}'
            user = cache.get(cache_key)
            
            if not user:
                try:
                    user = self.client.user(user_id)
                    cache.set(cache_key, user, self.CACHE_TTL)
                except JIRAError as e:
                    logger.warning(f"Could not find user {user_id}: {str(e)}")
                    continue
                    
            user_info[user_id] = user
        
        # Add mentions at the start of the comment
        mentions_text = ' '.join(f'[~{uid}]' for uid in mentions if uid in user_info)
        return f"{mentions_text} {comment}" if mentions_text else comment
    
    def add_comment_to_issue(self, issue_key: str, comment: str, 
                            mentions: Optional[List[str]] = None,
                            internal: bool = False) -> Dict[str, Any]:
        """
        Add a comment to a Jira issue with optional @mentions.
        
        Args:
            issue_key: The issue key (e.g., 'PROJECT-123')
            comment: The comment text
            mentions: Optional list of Jira user IDs to @mention
            internal: If True, marks the comment as internal (only visible to Jira users)
            
        Returns:
            Dict containing the created comment information
            
        Raises:
            ValidationError: If the issue key is invalid
            JiraClientError: If there's an error adding the comment
        """
        try:
            # Validate issue key
            self._validate_issue_key(issue_key)
            
            # Format comment with mentions
            formatted_comment = self._format_mentions(comment, mentions)
            
            # Get the issue first to verify it exists and we have access
            try:
                issue = self.client.issue(issue_key)
            except JIRAError as e:
                if e.status_code == 404:
                    raise ValidationError(f"Issue {issue_key} not found")
                elif e.status_code == 403:
                    raise JiraClientError("Permission denied to access the issue", status_code=403)
                raise
            
            # Add the comment
            comment_obj = self.client.add_comment(
                issue_key,
                formatted_comment,
                visibility={'type': 'role', 'value': 'Developers'} if internal else None
            )
            
            # Format the response
            response = {
                'id': comment_obj.id,
                'body': comment_obj.body,
                'author': {
                    'name': comment_obj.author.displayName,
                    'email': comment_obj.author.emailAddress,
                    'avatar': comment_obj.author.avatarUrls['48x48']
                },
                'created': comment_obj.created,
                'updated': comment_obj.updated,
                'visibility': 'internal' if internal else 'public'
            }
            
            logger.info(f"Successfully added comment to {issue_key}")
            return response
            
        except JIRAError as e:
            if e.status_code == 400:
                raise ValidationError(f"Invalid comment format: {str(e)}")
            raise JiraClientError(f"Error adding comment: {str(e)}", status_code=e.status_code)
        except Exception as e:
            raise JiraClientError(f"Unexpected error adding comment: {str(e)}")
            
    def update_issue_status(self, issue_key: str, new_status: str) -> Dict[str, Any]:
        """
        Update the status of a Jira issue.
        
        Args:
            issue_key: The issue key (e.g., 'PROJECT-123')
            new_status: The desired new status
            
        Returns:
            Dict containing the issue information after status update
            
        Raises:
            ValidationError: If the issue key is invalid or status transition is not allowed
            JiraClientError: If there's an error updating the issue
        """
        try:
            # Validate issue key
            self._validate_issue_key(issue_key)
            
            # Get the issue
            try:
                issue = self.client.issue(issue_key)
            except JIRAError as e:
                if e.status_code == 404:
                    raise ValidationError(f"Issue {issue_key} not found")
                elif e.status_code == 403:
                    raise JiraClientError("Permission denied to access the issue", status_code=403)
                raise
                
            # Get available transitions
            transitions = self.client.transitions(issue)
            valid_transitions = {t['name'].lower(): t['id'] for t in transitions}
            
            # Find matching transition
            new_status_lower = new_status.lower()
            transition_id = None
            
            # Try exact match first
            if new_status_lower in valid_transitions:
                transition_id = valid_transitions[new_status_lower]
            else:
                # Try partial match
                for status_name, t_id in valid_transitions.items():
                    if new_status_lower in status_name:
                        transition_id = t_id
                        break
            
            if not transition_id:
                valid_statuses = list(valid_transitions.keys())
                raise ValidationError(
                    f"Invalid status transition. Valid statuses are: {', '.join(valid_statuses)}"
                )
            
            # Perform the transition
            self.client.transition_issue(issue, transition_id)
            
            # Get updated issue
            updated_issue = self.client.issue(issue_key)
            
            # Format response
            response = {
                'key': updated_issue.key,
                'summary': updated_issue.fields.summary,
                'status': updated_issue.fields.status.name,
                'updated': str(updated_issue.fields.updated),
                'previous_status': issue.fields.status.name
            }
            
            logger.info(f"Successfully updated {issue_key} status to {new_status}")
            return response
            
        except JIRAError as e:
            if e.status_code == 400:
                raise ValidationError(f"Invalid status transition: {str(e)}")
            raise JiraClientError(f"Error updating issue status: {str(e)}", status_code=e.status_code)
        except Exception as e:
            raise JiraClientError(f"Unexpected error updating issue status: {str(e)}")
            
    def create_issue(self, project_key: str, summary: str, description: str,
                     issue_type: str, assignee: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Jira issue.
        
        Args:
            project_key: The project key (e.g., 'PROJECT')
            summary: Issue summary/title
            description: Detailed description of the issue
            issue_type: Type of issue (e.g., 'Bug', 'Task')
            assignee: Optional Jira user ID to assign the issue to
            
        Returns:
            Dict containing the created issue information
            
        Raises:
            ValidationError: If required fields are missing or invalid
            JiraClientError: If there's an error creating the issue
        """
        try:
            # Validate required fields
            if not project_key:
                raise ValidationError("Project key is required")
            if not summary:
                raise ValidationError("Summary is required")
            if not issue_type:
                raise ValidationError("Issue type is required")
                
            # Prepare issue fields
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description or '',
                'issuetype': {'name': issue_type}
            }
            
            # Add assignee if provided
            if assignee:
                try:
                    # Verify user exists
                    user = self.client.user(assignee)
                    issue_dict['assignee'] = {'name': user.name}
                except JIRAError as e:
                    if e.status_code == 404:
                        raise ValidationError(f"Assignee {assignee} not found")
                    raise
            
            # Create the issue
            new_issue = self.client.create_issue(fields=issue_dict)
            
            # Format response
            response = {
                'key': new_issue.key,
                'summary': new_issue.fields.summary,
                'description': new_issue.fields.description,
                'issue_type': new_issue.fields.issuetype.name,
                'status': new_issue.fields.status.name,
                'created': str(new_issue.fields.created),
                'updated': str(new_issue.fields.updated)
            }
            
            # Add assignee info if present
            if hasattr(new_issue.fields, 'assignee') and new_issue.fields.assignee:
                response['assignee'] = {
                    'name': new_issue.fields.assignee.displayName,
                    'email': new_issue.fields.assignee.emailAddress,
                    'avatar': new_issue.fields.assignee.avatarUrls['48x48']
                }
            
            logger.info(f"Successfully created issue {new_issue.key}")
            return response
            
        except JIRAError as e:
            if e.status_code == 400:
                raise ValidationError(f"Invalid issue data: {str(e)}")
            elif e.status_code == 403:
                raise JiraClientError("Permission denied to create issue", status_code=403)
            raise JiraClientError(f"Error creating issue: {str(e)}", status_code=e.status_code)
        except Exception as e:
            raise JiraClientError(f"Unexpected error creating issue: {str(e)}")
            
    def get_all_statuses(self) -> List[Dict[str, str]]:
        """
        Get all available statuses in Jira.
        
        Returns:
            List of dictionaries containing status information
            
        Raises:
            JiraClientError: If there's an error fetching statuses
        """
        try:
            # Get all statuses
            statuses = self.client.statuses()
            
            # Format response
            formatted_statuses = [{
                'id': status.id,
                'name': status.name,
                'description': status.description or '',
                'category': status.statusCategory.name,
                'color': status.statusCategory.colorName
            } for status in statuses]
            
            # Sort by category and name
            formatted_statuses.sort(key=lambda x: (x['category'], x['name']))
            
            logger.info(f"Successfully fetched {len(formatted_statuses)} statuses")
            return formatted_statuses
            
        except JIRAError as e:
            if e.status_code == 403:
                raise JiraClientError("Permission denied to fetch statuses", status_code=403)
            raise JiraClientError(f"Error fetching statuses: {str(e)}", status_code=e.status_code)
        except Exception as e:
            raise JiraClientError(f"Unexpected error fetching statuses: {str(e)}")
            
    def search_users(self, query: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for Jira users based on a query string.
        If query is empty or None, returns all users (up to max_results).
        
        Args:
            query: Optional search string for username/email
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing user information
            
        Raises:
            JiraClientError: If there's an error searching users
        """
        try:
            # Search users
            if query:
                users = self.client.search_users(query, maxResults=max_results)
            else:
                # If no query, get all users
                users = self.client.search_users('', maxResults=max_results)
            
            # Format response
            formatted_users = [{
                'account_id': user.accountId,
                'name': user.displayName,
                'email': getattr(user, 'emailAddress', ''),  # Some users might not have email visible
                'active': user.active,
                'avatar': user.avatarUrls['48x48'],
                'time_zone': getattr(user, 'timeZone', None)  # Optional field
            } for user in users if hasattr(user, 'accountId')  # Filter out system accounts
            ]
            
            # Sort by name
            formatted_users.sort(key=lambda x: x['name'])
            
            logger.info(f"Successfully found {len(formatted_users)} users for query: {query or 'all'}")
            return formatted_users
            
        except JIRAError as e:
            if e.status_code == 403:
                raise JiraClientError("Permission denied to search users", status_code=403)
            raise JiraClientError(f"Error searching users: {str(e)}", status_code=e.status_code)
        except Exception as e:
            raise JiraClientError(f"Unexpected error searching users: {str(e)}")
