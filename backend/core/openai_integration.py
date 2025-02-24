from openai import OpenAI
from django.conf import settings
from typing import Dict, Any, List, Optional, Union
import logging
from .api_utils import retry_with_backoff, format_error_message

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key: str = None):
        """
        Initialize the OpenAI client with API key.
        If not provided, the key will be loaded from environment variables.
        """
        try:
            self.api_key = api_key or settings.OPENAI_API_KEY
            # Add explicit configuration with timeout
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=30,  # Add timeout
                max_retries=3  # Explicit retries
            )
            
            # Test connectivity immediately
            logger.info("Verifying OpenAI connection...")
            self.client.models.list()  # Lightweight API call
            logger.info("OpenAI client initialized successfully")

    
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise Exception(f"Failed to initialize OpenAI client: {str(e)}")

    # Function specifications for Jira operations
    FUNCTION_SPECS = [
        {
            "name": "get_user_issues",
            "description": "Fetch issues assigned to a specific user in Jira, optionally filtered by status.",
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
                    }
                },
                "required": ["jira_user_id"]
            }
        },
        {
            "name": "add_comment_to_issue",
            "description": "Add a comment to a Jira issue, optionally mentioning users.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The key of the Jira issue"
                    },
                    "comment": {
                        "type": "string",
                        "description": "The comment text to add"
                    },
                    "mentions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of user IDs to mention"
                    }
                },
                "required": ["issue_key", "comment"]
            }
        },
        {
            "name": "update_issue_status",
            "description": "Update the status of a Jira issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The key of the Jira issue"
                    },
                    "new_status": {
                        "type": "string",
                        "description": "The new status to set for the issue"
                    }
                },
                "required": ["issue_key", "new_status"]
            }
        },
        {
            "name": "create_issue",
            "description": "Create a new issue in Jira.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "The project key where the issue will be created"
                    },
                    "summary": {
                        "type": "string",
                        "description": "The summary/title of the issue"
                    },
                    "description": {
                        "type": "string",
                        "description": "The detailed description of the issue"
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "The type of issue to create"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Optional user ID to assign the issue to"
                    }
                },
                "required": ["project_key", "summary", "description", "issue_type"]
            }
        },
        {
            "name": "get_all_statuses",
            "description": "Fetch all available statuses in Jira.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "search_users",
            "description": "Search for users in Jira. If query is empty, returns all users.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional search query to filter users"
                    }
                }
            }
        }
    ]

    @retry_with_backoff(max_retries=3)
    def get_intent_and_parameters(
        self, user_message: str, conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Analyze user message and conversation history to determine intent and extract parameters.
        Returns either a function call specification or a text response.
        """
        try:
            logger.info(f"Processing user message: {user_message[:50]}...")
            
            # Construct messages for the API call
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that interacts with Jira. "
                    "Your role is to understand user requests and either provide information "
                    "or help them perform actions in Jira."
                }
            ]

            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or another appropriate model
                messages=messages,
                functions=self.FUNCTION_SPECS,
                function_call="auto"
            )

            # Process the response
            message = response.choices[0].message

            # Check if the model wants to call a function
            if message.function_call:
                logger.info(f"Function call detected: {message.function_call.name}")
                return {
                    "function_name": message.function_call.name,
                    "arguments": eval(message.function_call.arguments)  # Safely parse JSON arguments
                }
            
            # If no function call, return the text response
            logger.info("Returning text response")
            return {"response": message.content}

        except Exception as e:
            logger.error(f"Error processing message with OpenAI: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])

    @retry_with_backoff(max_retries=2)
    def summarize_text(self, text: str, max_tokens: int = 100) -> str:
        """
        Generate a concise summary of the provided text using OpenAI.
        """
        try:
            logger.info(f"Generating summary for text of length {len(text)}")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or another appropriate model
                messages=[
                    {
                        "role": "system",
                        "content": f"Please summarize the following text in no more than {max_tokens} tokens:"
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=max_tokens
            )

            summary = response.choices[0].message.content
            logger.info("Summary generated successfully")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            error_info = format_error_message(e)
            raise Exception(error_info['error'])