from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock, call
from core.jira_integration import JiraClient, JIRAError, JiraClientError
from decouple import config
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
import os

# Ensure TESTING setting exists
if not hasattr(settings, 'TESTING'):
    settings.TESTING = True

class TestJiraClient(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set environment variables for testing
        os.environ['JIRA_SERVER_URL'] = 'https://test-jira.example.com'
        os.environ['JIRA_USER_EMAIL'] = 'test@example.com'
        os.environ['JIRA_API_TOKEN'] = 'test-token'

    def setUp(self):
        # Clear cache before each test
        cache.clear()
        
        # Create mock issue
        self.mock_issue = MagicMock()
        self.mock_issue.key = 'TEST-123'
        self.mock_issue.fields.summary = 'Test Issue'
        self.mock_issue.fields.status.name = 'To Do'
        self.mock_issue.fields.description = 'Test Description'
        
        # Create patcher for JIRA
        self.jira_patcher = patch('core.jira_integration.JIRA')
        self.mock_jira = self.jira_patcher.start()
        
        # Mock the JIRA client's myself() method to avoid caching issues
        mock_user = MagicMock()
        mock_user.displayName = 'Test User'
        mock_user.key = 'test-user'
        self.mock_jira.return_value.myself = MagicMock(return_value=mock_user)
        
        # Setup other mock methods
        self.mock_jira.return_value.search_issues = MagicMock()
        self.mock_jira.return_value.add_comment = MagicMock()
        self.mock_jira.return_value.transitions = MagicMock()
        self.mock_jira.return_value.create_issue = MagicMock()
        self.mock_jira.return_value.statuses = MagicMock()
        self.mock_jira.return_value.search_users = MagicMock()
        
        # Create client after setting up mock
        self.jira_client = JiraClient()
        
    def tearDown(self):
        self.jira_patcher.stop()
        cache.clear()
        
    @classmethod
    def tearDownClass(cls):
        # Clean up environment variables
        for key in ['JIRA_SERVER_URL', 'JIRA_USER_EMAIL', 'JIRA_API_TOKEN']:
            if key in os.environ:
                del os.environ[key]
        super().tearDownClass()

    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_get_user_issues(self, mock_cache_set, mock_cache_get):
        """Test fetching user issues"""
        # Create mock search results
        mock_results = MagicMock()
        mock_results.issues = [self.mock_issue]
        self.mock_jira.return_value.search_issues.return_value = mock_results
        mock_cache_get.return_value = None
        
        # Mock statuses
        mock_status1 = MagicMock()
        mock_status1.name = 'To Do'
        mock_status2 = MagicMock()
        mock_status2.name = 'In Progress'
        mock_status3 = MagicMock()
        mock_status3.name = 'Done'
        self.mock_jira.return_value.statuses.return_value = [mock_status1, mock_status2, mock_status3]
        
        # Test without status filter
        issues = self.jira_client.get_user_issues('test_user')
        self.assertEqual(len(issues), 1)
        self.mock_jira.return_value.search_issues.assert_called_with(
            'assignee = "test_user" ORDER BY updated DESC',
            startAt=0, maxResults=50, expand=[]
        )
        
        # Test with status filter
        issues = self.jira_client.get_user_issues('test_user', status='In Progress')
        self.mock_jira.return_value.search_issues.assert_called_with(
            'assignee = "test_user" AND status = "In Progress" ORDER BY updated DESC',
            startAt=0, maxResults=50, expand=[]
        )

    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_add_comment_to_issue(self, mock_cache_set, mock_cache_get):
        """Test adding comment to an issue"""
        # Setup mocks
        self.mock_jira.return_value.add_comment.return_value = MagicMock()
        mock_cache_get.return_value = None  # Simulate cache miss
        
        # Mock user lookup
        mock_user1 = MagicMock()
        mock_user1.name = 'user1'
        mock_user2 = MagicMock()
        mock_user2.name = 'user2'
        
        def mock_user_side_effect(user_id):
            if user_id == 'user1':
                return mock_user1
            elif user_id == 'user2':
                return mock_user2
            raise JIRAError()
            
        self.mock_jira.return_value.user = MagicMock(side_effect=mock_user_side_effect)
        
        # Test without mentions
        self.jira_client.add_comment_to_issue('TEST-123', 'Test comment')
        self.mock_jira.return_value.add_comment.assert_called_with('TEST-123', 'Test comment', visibility=None)
        
        # Test with mentions
        self.jira_client.add_comment_to_issue('TEST-123', 'Test comment', mentions=['user1', 'user2'])
        self.mock_jira.return_value.add_comment.assert_called_with(
            'TEST-123', '[~user1] [~user2] Test comment', visibility=None
        )
        
        # Verify cache operations
        mock_cache_get.assert_has_calls([
            call('jira_user_user1'),
            call('jira_user_user2')
        ])
        mock_cache_set.assert_has_calls([
            call('jira_user_user1', mock_user1, self.jira_client.CACHE_TTL),
            call('jira_user_user2', mock_user2, self.jira_client.CACHE_TTL)
        ])

    def test_update_issue_status(self):
        """Test updating issue status"""
        # Mock the current issue
        mock_issue = MagicMock()
        mock_issue.fields.status.name = 'To Do'
        self.mock_jira.return_value.issue.return_value = mock_issue
        
        # Create mock transitions
        mock_transitions = [
            {'id': '21', 'name': 'In Progress'},
            {'id': '31', 'name': 'Done'}
        ]
        self.mock_jira.return_value.transitions.return_value = mock_transitions
        
        # Test successful status update
        result = self.jira_client.update_issue_status('TEST-123', 'In Progress')
        self.assertEqual(result['key'], mock_issue.key)
        self.mock_jira.return_value.transition_issue.assert_called_with(mock_issue, '21')
        
        # Test invalid status
        with self.assertRaises(JiraClientError) as cm:
            self.jira_client.update_issue_status('TEST-123', 'Invalid Status')
        self.assertIn('in progress, done', str(cm.exception).lower())

    def test_create_issue(self):
        """Test creating a new issue"""
        self.mock_jira.return_value.create_issue.return_value = self.mock_issue
        
        result = self.jira_client.create_issue(
            project_key='TEST',
            summary='Test Issue',
            description='Test Description',
            issue_type='Task'
        )
        
        self.assertEqual(result['key'], 'TEST-123')
        self.mock_jira.return_value.create_issue.assert_called_once_with(
            fields={
                'project': {'key': 'TEST'},
                'summary': 'Test Issue',
                'description': 'Test Description',
                'issuetype': {'name': 'Task'}
            }
        )

    def test_get_all_statuses(self):
        """Test fetching all statuses"""
        mock_status = MagicMock()
        mock_status.name = 'To Do'
        self.mock_jira.return_value.statuses.return_value = [mock_status]
        
        statuses = self.jira_client.get_all_statuses()
        self.assertIn('To Do', [s['name'] for s in statuses])
        self.mock_jira.return_value.statuses.assert_called_once()

    def test_search_users(self):
        """Test searching users"""
        mock_user = MagicMock()
        mock_user.displayName = 'Test User'
        mock_user.emailAddress = 'test@example.com'
        self.mock_jira.return_value.search_users.return_value = [mock_user]
        
        # Test with query
        users = self.jira_client.search_users('test')
        self.mock_jira.return_value.search_users.assert_called_with('test', maxResults=50)
        self.assertEqual(len(users), 1)
        
        # Test without query (all users)
        users = self.jira_client.search_users(None)
        self.mock_jira.return_value.search_users.assert_called_with('', maxResults=50)
