import os
import logging
from typing import Dict, List, Optional, Any, Union
from openai import OpenAI
from openai import OpenAIError

logger = logging.getLogger(__name__)

class OpenAIClientError(Exception):
    """Base exception class for OpenAI client errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class OpenAIClient:
    """Client for interacting with OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment.
        
        Raises:
            OpenAIClientError: If API key is not provided and not in environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise OpenAIClientError("OpenAI API key not provided")
            
        self.client = OpenAI(api_key=self.api_key)
        
        # Default model settings
        self.model = "gpt-4"  # Using GPT-4 for better function calling capabilities
        self.temperature = 0.7
        self.max_tokens = 1000
        
        logger.info("OpenAI client initialized")
        
        # Define function specifications for OpenAI function calling
        self.function_specs = [
            {
                "name": "get_user_issues",
                "description": "Get Jira issues assigned to a specific user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jira_user_id": {
                            "type": "string",
                            "description": "The Jira user ID to fetch issues for"
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status to filter issues by"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of issues to return"
                        }
                    },
                    "required": ["jira_user_id"]
                }
            },
            {
                "name": "add_comment_to_issue",
                "description": "Add a comment to a Jira issue with optional @mentions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The issue key (e.g., 'PROJECT-123')"
                        },
                        "comment": {
                            "type": "string",
                            "description": "The comment text"
                        },
                        "mentions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of Jira user IDs to @mention"
                        },
                        "internal": {
                            "type": "boolean",
                            "description": "If true, marks the comment as internal (only visible to Jira users)"
                        }
                    },
                    "required": ["issue_key", "comment"]
                }
            },
            {
                "name": "update_issue_status",
                "description": "Update the status of a Jira issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The issue key (e.g., 'PROJECT-123')"
                        },
                        "new_status": {
                            "type": "string",
                            "description": "The desired new status"
                        }
                    },
                    "required": ["issue_key", "new_status"]
                }
            },
            {
                "name": "create_issue",
                "description": "Create a new Jira issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_key": {
                            "type": "string",
                            "description": "The project key (e.g., 'PROJECT')"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Issue summary/title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the issue"
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Type of issue (e.g., 'Bug', 'Task')"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Optional Jira user ID to assign the issue to"
                        }
                    },
                    "required": ["project_key", "summary", "issue_type"]
                }
            },
            {
                "name": "get_all_statuses",
                "description": "Get all available statuses in Jira",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "search_users",
                "description": "Search for Jira users based on a query string",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Optional search string for username/email"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    }
                }
            }
        ]
        
    def get_intent_and_parameters(self, user_message: str,
                                conversation_history: Optional[List[Dict[str, str]]] = None
                                ) -> Dict[str, Any]:
        """
        Analyze user message to determine intent and extract parameters for Jira operations.
        
        Args:
            user_message: The current user message
            conversation_history: Optional list of previous messages in the format:
                                [{'role': 'user|assistant', 'content': 'message'}]
        
        Returns:
            Dict containing either:
            - {'function_name': str, 'arguments': dict} for function calls
            - {'response': str} for text responses
        
        Raises:
            OpenAIClientError: If there's an error calling OpenAI API
        """
        try:
            # Prepare messages for the API call
            messages = [{
                'role': 'system',
                'content': (
                    "You are a helpful assistant that interacts with Jira. "
                    "Your role is to understand user requests and either: "
                    "1. Call an appropriate Jira function with the correct parameters, or "
                    "2. Respond directly if no Jira operation is needed."
                )
            }]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
                
            # Add current user message
            messages.append({
                'role': 'user',
                'content': user_message
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.function_specs,
                function_call='auto',
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Get the assistant's message
            assistant_message = response.choices[0].message
            
            # Check if the model wants to call a function
            if assistant_message.get('function_call'):
                function_call = assistant_message['function_call']
                return {
                    'function_name': function_call['name'],
                    'arguments': eval(function_call['arguments'])  # Safe since we control the input
                }
            
            # If no function call, return the text response
            return {'response': assistant_message['content']}
            
        except OpenAIError as e:
            raise OpenAIClientError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise OpenAIClientError(f"Unexpected error: {str(e)}")
            
    def summarize_text(self, text: str, max_tokens: int = 100) -> str:
        """
        Summarize a piece of text using OpenAI's API.
        
        Args:
            text: The text to summarize
            max_tokens: Maximum number of tokens in the summary
            
        Returns:
            A concise summary of the input text
            
        Raises:
            OpenAIClientError: If there's an error calling OpenAI API
        """
        try:
            if not text.strip():
                return ""
                
            # Prepare the prompt
            messages = [
                {
                    'role': 'system',
                    'content': (
                        "You are a helpful assistant that creates concise summaries. "
                        "Focus on the key points and maintain a professional tone. "
                        "If the text is technical, preserve important technical details."
                    )
                },
                {
                    'role': 'user',
                    'content': f"Please summarize the following text:\n\n{text}"
                }
            ]
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.5  # Lower temperature for more focused summaries
            )
            
            # Extract and return the summary
            summary = response.choices[0].message['content'].strip()
            
            logger.info(f"Successfully generated summary of length {len(summary)}")
            return summary
            
        except OpenAIError as e:
            raise OpenAIClientError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise OpenAIClientError(f"Unexpected error summarizing text: {str(e)}")
