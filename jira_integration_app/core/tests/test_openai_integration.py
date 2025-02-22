from django.test import TestCase
from unittest.mock import patch, MagicMock
from core.openai_integration import OpenAIClient
from django.conf import settings
import os

class TestOpenAIClient(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set environment variables for testing
        os.environ['OPENAI_API_KEY'] = 'test-openai-key'

    def setUp(self):
        # Create patcher for OpenAI client
        self.client_patcher = patch('core.openai_integration.OpenAI')
        self.mock_client = self.client_patcher.start()
        
        # Mock chat completions
        self.mock_chat = MagicMock()
        self.mock_completions = MagicMock()
        self.mock_completions.create = MagicMock()
        self.mock_chat.completions = self.mock_completions
        self.mock_client.return_value = MagicMock(chat=self.mock_chat)
        
        # Initialize client after mock setup
        self.openai_client = OpenAIClient()
        
        self.test_conversation_history = [
            {"role": "user", "content": "Show me my Jira issues"},
            {"role": "assistant", "content": "I'll help you find your Jira issues"}
        ]
        
    def tearDown(self):
        self.client_patcher.stop()
        
    @classmethod
    def tearDownClass(cls):
        # Clean up environment variables
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        super().tearDownClass()

    def test_get_intent_and_parameters_function_call(self):
        """Test getting intent with function call response"""
        # Mock OpenAI response for function call
        mock_choice = MagicMock()
        mock_choice.message = {
            'role': 'assistant',
            'content': None,
            'function_call': {
                'name': 'get_user_issues',
                'arguments': '{"jira_user_id": "USER123"}'
            }
        }
        mock_response = MagicMock(choices=[mock_choice])
        self.mock_completions.create.return_value = mock_response

        result = self.openai_client.get_intent_and_parameters(
            "Show me my issues",
            self.test_conversation_history
        )

        self.assertEqual(result['function_name'], 'get_user_issues')
        self.assertEqual(result['arguments']['jira_user_id'], 'USER123')
        self.mock_completions.create.assert_called_once()

    def test_get_intent_and_parameters_text_response(self):
        """Test getting intent with text response"""
        # Mock OpenAI response for text response
        mock_choice = MagicMock()
        mock_choice.message = {
            'role': 'assistant',
            'content': 'I can help you with that',
            'function_call': None
        }
        mock_response = MagicMock(choices=[mock_choice])
        self.mock_completions.create.return_value = mock_response

        result = self.openai_client.get_intent_and_parameters(
            "What can you do?",
            self.test_conversation_history
        )

        self.assertEqual(result['response'], "I can help you with that")
        self.mock_completions.create.assert_called_once()

    def test_summarize_text(self):
        """Test text summarization"""
        test_text = "This is a long text that needs to be summarized."
        mock_choice = MagicMock()
        mock_choice.message = {
            'role': 'assistant',
            'content': 'Summarized text',
            'function_call': None
        }
        mock_response = MagicMock(choices=[mock_choice])
        self.mock_completions.create.return_value = mock_response

        summary = self.openai_client.summarize_text(test_text, max_tokens=50)
        
        self.assertEqual(summary, "Summarized text")
        self.mock_completions.create.assert_called_once()

    def test_function_specifications(self):
        """Test that function specifications are properly defined"""
        specs = self.openai_client.function_specs
        
        # Check if all required functions are defined
        required_functions = [
            'get_user_issues',
            'add_comment_to_issue',
            'update_issue_status',
            'create_issue',
            'get_all_statuses',
            'search_users'
        ]
        
        defined_functions = [spec['name'] for spec in specs]
        for func in required_functions:
            self.assertIn(func, defined_functions)
        
        # Check structure of function specifications
        for spec in specs:
            self.assertIn('name', spec)
            self.assertIn('description', spec)
            self.assertIn('parameters', spec)
            self.assertIsInstance(spec['parameters'], dict)
