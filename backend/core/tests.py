from django.test import TestCase
from requests.exceptions import RequestException
from jira.exceptions import JIRAError
from openai import OpenAIError, RateLimitError, APIError
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from core import views, jira_integration, openai_integration, api_utils
from core.api_utils import retry_with_backoff, get_retry_after, format_error_message
from core.models import UserProfile
from django.urls import reverse
import uuid

# -------------------------------
# Tests for core/api_utils.py
# -------------------------------
class ApiUtilsTests(TestCase):
    def test_retry_with_backoff_success(self):
        mock_func = MagicMock(return_value='success')
        decorated_func = retry_with_backoff()(mock_func)
        result = decorated_func()
        self.assertEqual(result, 'success')
        mock_func.assert_called_once()

    def test_retry_with_backoff_with_request_exception(self):
        mock_func = MagicMock(side_effect=[RequestException(), 'success'])
        decorated_func = retry_with_backoff(max_retries=2)(mock_func)
        result = decorated_func()
        self.assertEqual(result, 'success')
        self.assertEqual(mock_func.call_count, 2)

    def test_retry_with_backoff_with_rate_limit(self):
        mock_response = MagicMock(status_code=429, headers={'Retry-After': '0.1'})
        rate_limit_error = RateLimitError(message='Rate limit exceeded', response=mock_response, body={})
        rate_limit_error.retry_after = 0.1
        mock_func = MagicMock(side_effect=[rate_limit_error, 'success'])
        decorated_func = retry_with_backoff(max_retries=2)(mock_func)
        result = decorated_func()
        self.assertEqual(result, 'success')
        self.assertEqual(mock_func.call_count, 2)

    def test_retry_with_backoff_max_retries_exceeded(self):
        mock_func = MagicMock(side_effect=RequestException('test error'))
        decorated_func = retry_with_backoff(max_retries=2)(mock_func)
        with self.assertRaises(RequestException):
            decorated_func()
        self.assertEqual(mock_func.call_count, 2)

    def test_get_retry_after_openai(self):
        mock_response = MagicMock(status_code=429, headers={'Retry-After': '30'})
        error = RateLimitError(message='Rate limit exceeded', response=mock_response, body={})
        error.retry_after = 30
        retry_after = get_retry_after(error)
        self.assertEqual(retry_after, 30.0)

    def test_get_retry_after_jira(self):
        error = JIRAError()
        error.status_code = 429
        error.response = MagicMock()
        error.response.headers = {'Retry-After': '60'}
        retry_after = get_retry_after(error)
        self.assertEqual(retry_after, 60.0)

    def test_format_error_message_jira_404(self):
        error = JIRAError(status_code=404)
        result = format_error_message(error)
        self.assertEqual(result['error'], 'The requested Jira resource was not found.')

    def test_format_error_message_jira_401(self):
        error = JIRAError(status_code=401)
        result = format_error_message(error)
        self.assertEqual(result['error'], 'Authentication failed. Please check your Jira credentials.')

    def test_format_error_message_openai_rate_limit(self):
        mock_response = MagicMock(status_code=429, headers={'Retry-After': '30'})
        error = RateLimitError(message='Rate limit exceeded', response=mock_response, body={})
        result = format_error_message(error)
        self.assertEqual(result['error'], 'OpenAI rate limit reached. Please try again later.')

    def test_format_error_message_generic_openai(self):
        error = OpenAIError()
        result = format_error_message(error)
        self.assertEqual(result['error'], 'An error occurred while processing your request with OpenAI.')

# -------------------------------
# Tests for core/views.py
# -------------------------------
class ViewsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Clean up any existing data
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        
        # Create test user and profile with unique user_id that will be shared across tests
        unique_id = uuid.uuid4()
        cls.user = User.objects.create_user(username=f'testuser_{unique_id}', password='testpass')
        cls.profile = UserProfile.objects.create(user=cls.user, jira_user_id=f'test123_{unique_id}')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.client.force_authenticate(user=None)

    @patch('core.openai_integration.OpenAI')
    @patch('core.jira_integration.JIRA')
    def test_chat_view_post_success(self, mock_jira, mock_openai):
        # Mock OpenAI client response
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content='Test response'))
        ]
        
        url = reverse('chat')
        data = {'message': 'test message'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_chat_view_post_invalid(self):
        url = reverse('chat')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_chat_view_get_not_allowed(self):
        url = reverse('chat')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_chat_view_missing_message(self):
        url = reverse('chat')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Message is required')

    def test_chat_view_missing_user_profile(self):
        # Delete the user profile
        self.profile.delete()
        url = reverse('chat')
        response = self.client.post(url, {'message': 'test'}, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'User profile not found')

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_chat_view_function_call_get_user_issues(self, mock_jira, mock_openai):
        mock_openai_instance = mock_openai.return_value
        mock_jira_instance = mock_jira.return_value

        # Mock OpenAI response
        mock_openai_instance.get_intent_and_parameters.return_value = {
            'function_name': 'get_user_issues',
            'arguments': {'user_id': 'test123'}
        }
        mock_jira_instance.get_user_issues.return_value = ['issue1', 'issue2']
        mock_openai_instance.summarize_text.return_value = 'Summary'

        url = reverse('chat')
        response = self.client.post(url, {'message': 'show my issues'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'issue_list')
        self.assertEqual(response.json()['summary'], 'Summary')

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_chat_view_function_call_error(self, mock_jira, mock_openai):
        mock_openai_instance = mock_openai.return_value
        mock_jira_instance = mock_jira.return_value

        # Mock OpenAI response
        mock_openai_instance.get_intent_and_parameters.return_value = {
            'function_name': 'get_user_issues',
            'arguments': {'user_id': 'test123'}
        }
        mock_jira_instance.get_user_issues.side_effect = JIRAError()

        url = reverse('chat')
        response = self.client.post(url, {'message': 'show my issues'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'text')
        self.assertTrue('An error occurred' in response.json()['content'])

    def test_initial_greeting(self):
        url = reverse('initial_greeting')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

# -------------------------------
# Tests for core/jira_integration.py
# -------------------------------
class JiraIntegrationTests(TestCase):
    @patch('core.jira_integration.settings')
    def setUp(self, mock_settings):
        # Mock settings
        mock_settings.JIRA_SERVER_URL = 'https://test.atlassian.net'
        mock_settings.JIRA_USER_EMAIL = 'test@example.com'
        mock_settings.JIRA_API_TOKEN = 'test-token'
        
        # Initialize client
        self.jira = jira_integration.JiraClient()
        self.jira.client = MagicMock()

    @patch('core.jira_integration.JIRA')
    def test_search_users_success(self, mock_jira):
        mock_user = MagicMock()
        mock_user.accountId = 'test-account-id'
        mock_user.displayName = 'John Doe'
        mock_user.emailAddress = 'john@example.com'
        self.jira.client.search_users.return_value = [mock_user]
        
        result = self.jira.search_users('john')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['account_id'], 'test-account-id')

    def test_search_users_failure(self):
        # Create a JIRAError with proper status code
        error = JIRAError(status_code=500, text='Jira API Error')
        self.jira.client.search_users.side_effect = error
        with self.assertRaises(Exception) as context:
            self.jira.search_users('john')
        self.assertIn('Jira Error (500)', str(context.exception))

    def test_search_users_empty(self):
        self.jira.client.search_users.return_value = []
        result = self.jira.search_users('nonexistent')
        self.assertEqual(result, [])

    def test_get_user_issues(self):
        # Create a complete mock issue
        mock_issue = MagicMock()
        mock_issue.key = 'PROJ-1'
        mock_issue.fields.summary = 'Test Issue'
        mock_issue.fields.status.name = 'Open'
        mock_issue.fields.description = 'Test Description'
        mock_issue.fields.created = '2025-02-25T04:28:57'
        mock_issue.fields.priority = MagicMock(name='High')
        mock_issue.fields.assignee = MagicMock(displayName='John Doe')
        mock_issue.fields.reporter = MagicMock(displayName='Jane Smith')
        mock_issue.fields.comment = MagicMock()
        mock_issue.fields.comment.comments = []
        
        self.jira.client.search_issues.return_value = [mock_issue]

        result = self.jira.get_user_issues('john_doe')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['key'], 'PROJ-1')
        self.assertEqual(result[0]['summary'], 'Test Issue')
        self.assertEqual(result[0]['status'], 'Open')
        self.assertEqual(result[0]['assignee'], 'John Doe')

    def test_get_issue(self):
        # Create a complete mock issue
        mock_issue = MagicMock()
        mock_issue.key = 'PROJ-1'
        mock_issue.fields.summary = 'Test Issue'
        mock_issue.fields.description = 'Test Description'
        mock_issue.fields.status = MagicMock(name='Open')
        mock_issue.fields.created = '2025-02-25T04:28:57'
        mock_issue.fields.priority = MagicMock(name='High')
        mock_issue.fields.assignee = MagicMock(displayName='John Doe')
        mock_issue.fields.reporter = MagicMock(displayName='Jane Smith')
        mock_issue.fields.comment = MagicMock()
        mock_issue.fields.comment.comments = []
        
        self.jira.client.issue.return_value = mock_issue

        result = self.jira.get_issue('PROJ-1')
        self.assertEqual(result['key'], 'PROJ-1')
        self.assertEqual(result['summary'], 'Test Issue')
        self.assertEqual(result['description'], 'Test Description')
        self.assertEqual(result['assignee'], 'John Doe')
        self.assertEqual(result['reporter'], 'Jane Smith')

    def test_add_comment(self):
        # Create a complete mock comment
        mock_comment = MagicMock()
        mock_comment.body = 'Test comment'
        mock_comment.author = MagicMock(displayName='John Doe')
        mock_comment.created = '2025-02-25T04:28:57'
        self.jira.client.add_comment.return_value = mock_comment

        result = self.jira.add_comment_to_issue('PROJ-1', 'Test comment')
        self.assertEqual(result['body'], 'Test comment')
        self.assertEqual(result['author'], 'John Doe')
        self.assertTrue('created' in result)

    def test_update_issue_status_success(self):
        # Mock the issue and transitions
        mock_issue = MagicMock()
        mock_issue.fields.status.name = 'In Progress'
        self.jira.client.issue.return_value = mock_issue
        self.jira.client.transitions.return_value = [
            {'id': '1', 'name': 'To Do'},
            {'id': '2', 'name': 'In Progress'},
            {'id': '3', 'name': 'Done'}
        ]

        result = self.jira.update_issue_status('PROJ-1', 'In Progress')
        self.assertEqual(result['status'], 'In Progress')
        self.assertEqual(result['key'], 'PROJ-1')
        self.assertTrue('message' in result)

    def test_update_issue_status_invalid_status(self):
        # Mock transitions without the requested status
        self.jira.client.transitions.return_value = [
            {'id': '1', 'name': 'To Do'},
            {'id': '2', 'name': 'Done'}
        ]

        with self.assertRaises(Exception) as context:
            self.jira.update_issue_status('PROJ-1', 'Invalid Status')
        self.assertIn('Invalid status', str(context.exception))

    def test_update_issue_status_error(self):
        # Mock transitions and then JIRAError when transitioning
        mock_issue = MagicMock()
        self.jira.client.issue.return_value = mock_issue
        self.jira.client.transitions.return_value = [
            {'id': '2', 'name': 'In Progress'}
        ]
        error = JIRAError(status_code=500, text='Jira API Error')
        self.jira.client.transition_issue.side_effect = error

        with self.assertRaises(Exception) as context:
            self.jira.update_issue_status('PROJ-1', 'In Progress')
        self.assertIn('Jira Error (500)', str(context.exception))

    def test_create_issue_success(self):
        # Mock new issue
        mock_issue = MagicMock()
        mock_issue.key = 'PROJ-1'
        mock_issue.fields.summary = 'Test Issue'
        mock_issue.fields.status.name = 'Open'
        mock_issue.fields.assignee = MagicMock(name='John Doe')
        self.jira.client.create_issue.return_value = mock_issue

        result = self.jira.create_issue(
            project_key='PROJ',
            summary='Test Issue',
            description='Test Description',
            issue_type='Task',
            assignee='john.doe'
        )
        self.assertEqual(result['key'], 'PROJ-1')
        self.assertEqual(result['summary'], 'Test Issue')
        self.assertEqual(result['status'], 'Open')

    def test_create_issue_missing_fields(self):
        with self.assertRaises(Exception):
            self.jira.create_issue(
                project_key='',
                summary='Test Issue',
                description='Test Description',
                issue_type='Task'
            )

    def test_create_issue_error(self):
        # Mock JIRAError when creating issue
        error = JIRAError(status_code=500, text='Jira API Error')
        self.jira.client.create_issue.side_effect = error

        with self.assertRaises(Exception) as context:
            self.jira.create_issue(
                project_key='PROJ',
                summary='Test Issue',
                description='Test Description',
                issue_type='Task'
            )
        self.assertIn('Jira Error (500)', str(context.exception))

    def test_get_all_statuses_success(self):
        # Mock statuses
        mock_status = MagicMock()
        mock_status.id = '1'
        mock_status.name = 'Open'
        mock_status.description = 'Issue is open'
        self.jira.client.statuses.return_value = [mock_status]

        result = self.jira.get_all_statuses()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], '1')
        self.assertEqual(result[0]['name'], 'Open')
        self.assertEqual(result[0]['description'], 'Issue is open')

    def test_get_all_statuses_error(self):
        # Mock JIRAError when fetching statuses
        error = JIRAError(status_code=500, text='Jira API Error')
        self.jira.client.statuses.side_effect = error

        with self.assertRaises(Exception) as context:
            self.jira.get_all_statuses()
        self.assertIn('Jira Error (500)', str(context.exception))

# -------------------------------
# Additional Tests for core/views.py
# -------------------------------

class LoginViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.login_url = reverse('token_obtain_pair')

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_login_missing_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue('error' in response.data)

class TokenRefreshViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.refresh_token = response.data['refresh']

    def test_token_refresh_success(self):
        response = self.client.post(self.refresh_url, {
            'refresh': self.refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_token_refresh_invalid(self):
        try:
            response = self.client.post(self.refresh_url, {
                'refresh': 'invalid-token'
            })
        except Exception as e:
            self.assertIn('Token is invalid or expired', str(e))
            return
        self.fail('Expected token refresh to fail')

class ChatViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user, jira_user_id='test123')
        self.login_url = reverse('token_obtain_pair')
        self.chat_url = reverse('chat')
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_chat_get_issue_success(self, mock_jira, mock_openai):
        # Mock OpenAI response
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.get_intent_and_parameters.return_value = {
            'function_name': 'get_issue',
            'arguments': {'issue_key': 'PROJ-1'}
        }
        mock_openai_instance.summarize_text.return_value = 'Issue summary'

        # Mock Jira response
        mock_jira_instance = mock_jira.return_value
        mock_jira_instance.get_issue.return_value = {
            'key': 'PROJ-1',
            'summary': 'Test Issue'
        }

        response = self.client.post(self.chat_url, {'message': 'Show me issue PROJ-1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'issue')

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_chat_create_issue_success(self, mock_jira, mock_openai):
        # Mock OpenAI response
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.get_intent_and_parameters.return_value = {
            'function_name': 'create_issue',
            'arguments': {
                'project_key': 'PROJ',
                'summary': 'New Issue',
                'description': 'Test Description',
                'issue_type': 'Task'
            }
        }
        mock_openai_instance.summarize_text.return_value = 'Issue created'

        # Mock Jira response
        mock_jira_instance = mock_jira.return_value
        mock_jira_instance.create_issue.return_value = {
            'key': 'PROJ-2',
            'summary': 'New Issue'
        }

        response = self.client.post(self.chat_url, {'message': 'Create a new task'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'new_issue')

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_chat_jira_error(self, mock_jira, mock_openai):
        # Mock OpenAI response
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.get_intent_and_parameters.return_value = {
            'function_name': 'get_issue',
            'arguments': {'issue_key': 'PROJ-1'}
        }

        # Mock Jira error
        mock_jira_instance = mock_jira.return_value
        mock_jira_instance.get_issue.side_effect = JIRAError(status_code=404, text='Issue not found')

        response = self.client.post(self.chat_url, {'message': 'Show me issue PROJ-1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'text')
        self.assertTrue('error' in response.data['content'].lower())

class InitialGreetingViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user, jira_user_id='test123')
        self.login_url = reverse('token_obtain_pair')
        self.greeting_url = reverse('initial_greeting')
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_greeting_success(self, mock_jira, mock_openai):
        # Mock OpenAI response
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content='1. Check your issues\n2. Create a task'))
        ]

        # Mock Jira response
        mock_jira_instance = mock_jira.return_value
        mock_jira_instance.client.user.return_value = MagicMock(displayName='Test User')
        mock_jira_instance.get_user_issues.return_value = [{'key': 'PROJ-1'}]

        response = self.client.get(self.greeting_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'greeting')
        self.assertTrue(len(response.data['suggestions']) > 0)

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_greeting_openai_error(self, mock_jira, mock_openai):
        # Mock OpenAI error
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.client.chat.completions.create.side_effect = Exception('OpenAI error')

        # Mock Jira response
        mock_jira_instance = mock_jira.return_value
        mock_jira_instance.client.user.return_value = MagicMock(displayName='Test User')

        response = self.client.get(self.greeting_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'greeting')
        self.assertTrue(len(response.data['suggestions']) == 3)  # Should use fallback suggestions

    @patch('core.views.OpenAIClient')
    @patch('core.views.JiraClient')
    def test_greeting_jira_error(self, mock_jira, mock_openai):
        # Mock OpenAI response
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content='1. Check your issues\n2. Create a task'))
        ]

        # Mock Jira error
        mock_jira_instance = mock_jira.return_value
        mock_jira_instance.client.user.side_effect = JIRAError(status_code=404, text='User not found')

        response = self.client.get(self.greeting_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'greeting')
        self.assertTrue(len(response.data['suggestions']) > 0)

# -------------------------------
# Tests for core/openai_integration.py
# -------------------------------
class OpenAIIntegrationTests(TestCase):
    @patch('core.openai_integration.OpenAI')
    def setUp(self, mock_openai_class):
        self.mock_openai = MagicMock()
        mock_openai_class.return_value = self.mock_openai
        self.mock_openai.models = MagicMock()
        self.mock_openai.models.list = MagicMock(return_value={'data': [{'id': 'test-model'}]})
        self.openai = openai_integration.OpenAIClient(api_key='test-key')

    @patch('core.openai_integration.OpenAI')
    def test_get_intent_and_parameters_success(self, _):
        mock_function_call = MagicMock()
        mock_function_call.name = 'get_user_issues'
        mock_function_call.arguments = '{"jira_user_id": "john", "status": "open"}'

        mock_message = MagicMock()
        mock_message.content = None
        mock_message.function_call = mock_function_call

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        self.mock_openai.chat.completions.create.return_value = mock_response
        result = self.openai.get_intent_and_parameters('Show me Johns open tickets', [], 'john')
        self.assertIsNotNone(result)
        self.assertEqual(result['function_name'], 'get_user_issues')

    @patch('core.openai_integration.OpenAI')
    def test_get_intent_and_parameters_error(self, _):
        self.mock_openai.chat.completions.create.side_effect = Exception('OpenAI API Error')
        with self.assertRaises(Exception):
            self.openai.get_intent_and_parameters('test prompt', [], None)

    @patch('core.openai_integration.OpenAI')
    def test_get_intent_and_parameters_invalid_response(self, _):
        mock_message = MagicMock()
        mock_message.content = 'Invalid response'
        mock_message.function_call = None

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        self.mock_openai.chat.completions.create.return_value = mock_response
        result = self.openai.get_intent_and_parameters('test prompt', [], None)
        self.assertIsNotNone(result)
        self.assertEqual(result['response'], 'Invalid response')

    def test_summarize_text(self):
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = 'Summary'
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        self.mock_openai.chat.completions.create.return_value = mock_response
        result = self.openai.summarize_text('Long text to summarize')
        self.assertEqual(result, 'Summary')

    def test_summarize_text_error(self):
        self.mock_openai.chat.completions.create.side_effect = Exception('OpenAI API Error')
        with self.assertRaises(Exception):
            self.openai.summarize_text('Text to summarize')
