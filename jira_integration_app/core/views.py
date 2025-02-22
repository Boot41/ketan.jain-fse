from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import LoginSerializer, UserSerializer
from .openai_integration import OpenAIClient, OpenAIClientError
from .jira_integration import JiraClient, JiraClientError
from .models import Conversation, ScrumUpdate
from .utils import get_scrum_update, create_scrum_update, format_scrum_update
from .exceptions import ScrumUpdateError, AuthenticationError, IntegrationError
from .notifications import NotificationManager
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, List
import re


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                raise AuthenticationError(
                    message='Invalid credentials',
                    code='invalid_credentials',
                    details=serializer.errors
                )
            
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            if not isinstance(e, AuthenticationError):
                raise AuthenticationError(
                    message='Authentication failed',
                    code='auth_error',
                    details={'original_error': str(e)}
                )


class ChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the user's message from request data
        message = request.data.get('message')
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the user's profile with Jira ID
            user_profile = request.user.profile
            if not user_profile.jira_user_id:
                return Response(
                    {'error': 'Jira user ID not configured for this user'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Initialize OpenAI and Jira clients
            openai_client = OpenAIClient()
            jira_client = JiraClient()

            # Check if we need to get scrum updates
            scrum_update = get_scrum_update(request.user)
            
            # Get conversation history
            conversation_history = list(Conversation.objects.filter(
                user=request.user
            ).order_by('-timestamp')[:10])
            
            # Format conversation history for OpenAI
            formatted_history = [
                {
                    'role': 'user' if msg.is_user_message else 'assistant',
                    'content': msg.message
                } for msg in reversed(conversation_history)
            ]
            
            # If no scrum update exists for today, prepend scrum context
            if not scrum_update:
                scrum_context = {
                    'role': 'system',
                    'content': (
                        "You are collecting the daily scrum update. Ask for these three things:\n"
                        "1. What did you do yesterday?\n"
                        "2. What will you do today?\n"
                        "3. Are there any blockers?\n\n"
                        "After collecting all three responses, compile them into a well-formatted update."
                    )
                }
                formatted_history.insert(0, scrum_context)
                
                # If this is the first message of the day, ask for scrum updates
                if not conversation_history:
                    formatted_history.append({
                        'role': 'assistant',
                        'content': "Good morning! Let's start with your daily scrum update. What did you work on yesterday?"
                    })

            # Get intent and parameters from OpenAI
            intent_result = openai_client.get_intent_and_parameters(
                message, 
                formatted_history
            )
            
            # Save user's message to conversation history
            Conversation.objects.create(
                user=request.user,
                message=message,
                is_user_message=True
            )

            # Check if we're collecting scrum updates and this is not a function call
            if not scrum_update and not isinstance(intent_result, dict):
                # Check if we have all three parts of the scrum update
                scrum_parts = [msg for msg in conversation_history if msg.is_user_message][-3:]
                if len(scrum_parts) >= 3:
                    # Compile the scrum update
                    full_update = format_scrum_update(
                        yesterday=scrum_parts[0].message,
                        today=scrum_parts[1].message,
                        blockers=scrum_parts[2].message
                    )
                    
                    # Create the scrum update and tag Jira issues
                    try:
                        scrum_update, jira_results = create_scrum_update(
                            user=request.user,
                            updates=full_update,
                            jira_client=jira_client
                        )
                        
                        # Check for any failed Jira updates
                        failed_issues = []
                        for result in jira_results:
                            if result.startswith("Failed to add comment to"):
                                issue_key = re.search(r'[A-Z]+-\d+', result).group(0)
                                failed_issues.append(issue_key)
                        
                        if failed_issues:
                            NotificationManager.notify_jira_sync_error(
                                user=request.user,
                                issue_keys=failed_issues,
                                error_message="Failed to add comments to some Jira issues"
                            )
                        
                        # Create a response message
                        response = "Thanks for providing your scrum update! I've saved it and "
                        if jira_results:
                            response += f"here's what I did with it:\n" + "\n".join(jira_results)
                        else:
                            response += "I didn't find any Jira issues to tag."
                    except Exception as e:
                        error_msg = str(e)
                        raise ScrumUpdateError(
                            message=f"Error saving scrum update: {error_msg}",
                            code='scrum_update_error',
                            details={'original_error': error_msg}
                        )
                    
                    # Save the response to conversation history
                    Conversation.objects.create(
                        user=request.user,
                        message=response,
                        is_user_message=False
                    )
                    
                    return Response({'message': response}, status=status.HTTP_200_OK)
            
            # If intent_result is a function call
            if isinstance(intent_result, dict) and 'function_name' in intent_result:
                function_name = intent_result['function_name']
                arguments = intent_result.get('arguments', {})
                
                # Add jira_user_id to arguments if not present and function needs it
                if function_name == 'get_user_issues' and 'jira_user_id' not in arguments:
                    arguments['jira_user_id'] = user_profile.jira_user_id

                # Map function names to JiraClient methods
                jira_function_map = {
                    'get_user_issues': jira_client.get_user_issues,
                    'add_comment_to_issue': jira_client.add_comment_to_issue,
                    'update_issue_status': jira_client.update_issue_status,
                    'create_issue': jira_client.create_issue,
                    'get_all_statuses': jira_client.get_all_statuses,
                    'search_users': jira_client.search_users
                }

                if function_name not in jira_function_map:
                    return Response(
                        {'error': f'Unknown function: {function_name}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    # Call the appropriate Jira function with the provided arguments
                    result = jira_function_map[function_name](**arguments)

                    # Construct a user-friendly response based on the function called
                    response_messages = {
                        'get_user_issues': 'Here are your Jira issues:',
                        'add_comment_to_issue': f'Added comment to issue {arguments.get("issue_key")}',
                        'update_issue_status': f'Updated status of issue {arguments.get("issue_key")} to {arguments.get("new_status")}',
                        'create_issue': f'Created new issue with key: {result}',
                        'get_all_statuses': 'Here are all available Jira statuses:',
                        'search_users': 'Here are the Jira users matching your search:'
                    }

                    response_message = response_messages.get(function_name, 'Operation completed successfully')
                except (OpenAIClientError, JiraClientError) as e:
                    raise IntegrationError(
                        message=str(e),
                        code='integration_error',
                        details={
                            'service': e.__class__.__name__,
                            'function': function_name,
                            'arguments': arguments
                        }
                    )
                    
                    # Save AI's response to conversation history
                    Conversation.objects.create(
                        user=request.user,
                        message=response_message,
                        is_user_message=False
                    )
                    
                    return Response({
                        'message': response_message,
                        'result': result
                    }, status=status.HTTP_200_OK)

                except JiraClientError as e:
                    return Response(
                        {'error': str(e)},
                        status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
                    )

            # If intent_result is a text response
            else:
                # Save AI's response to conversation history
                Conversation.objects.create(
                    user=request.user,
                    message=intent_result,
                    is_user_message=False
                )
                
                return Response(
                    {'message': intent_result},
                    status=status.HTTP_200_OK
                )

        except OpenAIClientError as e:
            return Response(
                {'error': f'OpenAI error: {str(e)}'}, 
                status=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        except JiraClientError as e:
            return Response(
                {'error': f'Jira error: {str(e)}'}, 
                status=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InitialGreetingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            greeting = f"Hi {user.get_full_name() or user.username}! Here are the top 3 things I can help you with today:\n\n"
            greeting += "1. Update the status of your Jira tickets.\n"
            greeting += "2. Get a summary of your assigned tickets.\n"
            greeting += "3. Add comments to your tickets.\n\n"
            greeting += "What would you like to do?"

            return Response(
                {'message': greeting},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': f'Error generating greeting: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
