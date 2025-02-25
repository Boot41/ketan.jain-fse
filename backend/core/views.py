import logging
import re

from jira import JIRAError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .models import UserProfile, Conversation
from .openai_integration import OpenAIClient
from .jira_integration import JiraClient

logger = logging.getLogger(__name__)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, 
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_message = request.data.get('message')
            if not user_message:
                return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

            Conversation.objects.create(user=request.user, message=user_message, is_user_message=True)

            conversation_history = [
                {'role': 'user' if msg.is_user_message else 'assistant', 'content': msg.message}
                for msg in Conversation.objects.filter(user=request.user).order_by('-timestamp')[:10][::-1]
            ]

            openai_client = OpenAIClient()
            jira_client = JiraClient()

            result = openai_client.get_intent_and_parameters(user_message, conversation_history,
                                                             user_profile.jira_user_id)

            # ---  Structured Response Handling (Modified) ---

            if "response" in result:
                # Text response
                response_data = {"type": "text", "content": result["response"]}
            elif "function_name" in result:
                function_name = result["function_name"]
                arguments = result["arguments"]

                try:
                    if function_name == "get_user_issues":
                        issues = jira_client.get_user_issues(**arguments)
                        summary = openai_client.summarize_text(str(issues))
                        response_data = {"type": "issue_list", "issues": issues, "summary": summary}
                    elif function_name == "get_issue":
                        issue = jira_client.get_issue(**arguments)
                        summary = openai_client.summarize_text(str(issue))
                        response_data = {"type": "issue", "issue": issue, "summary": summary}
                    elif function_name == "add_comment_to_issue":
                        comment = jira_client.add_comment_to_issue(**arguments)
                        summary = openai_client.summarize_text(str(comment))
                        response_data = {"type": "comment", "comment": comment, "summary": summary}
                    elif function_name == "update_issue_status":
                        result_data = jira_client.update_issue_status(**arguments)
                        summary = openai_client.summarize_text(str(result_data))
                        response_data = {"type": "status_update", "result": result_data, "summary": summary}
                    elif function_name == "create_issue":
                        new_issue = jira_client.create_issue(**arguments)
                        summary = openai_client.summarize_text(str(new_issue))
                        response_data = {"type": "new_issue", "issue": new_issue, "summary": summary}
                    elif function_name == "get_all_statuses":
                        statuses = jira_client.get_all_statuses()
                        summary = openai_client.summarize_text(str(statuses))
                        response_data = {"type": "status_list", "statuses": statuses, "summary": summary}
                    elif function_name == "search_users":
                        users = jira_client.search_users(**arguments)
                        summary = openai_client.summarize_text(str(users))
                        response_data = {"type": "user_list", "users": users, "summary": summary}
                    else:
                        response_data = {"type": "text", "content": "I'm sorry, I couldn't handle that request."}

                except Exception as e:
                    # Handle errors from Jira API calls
                    response_data = {"type": "text", "content": f"An error occurred: {str(e)}"}
            else:
                response_data = {"type": "text", "content": "I'm sorry, I couldn't understand the response."}

            # --- End of Structured Response Handling ---

            # Save AI response to conversation history
            Conversation.objects.create(
                user=request.user,
                message=response_data.get('summary') or response_data.get('content'),  # Save summary or content
                is_user_message=False
            )

            return Response(response_data, status=status.HTTP_200_OK)  # Return the structured response

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InitialGreetingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        openai_client = OpenAIClient()
        jira_client = JiraClient()
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            jira_user_id = user_profile.jira_user_id
        except UserProfile.DoesNotExist:
            jira_user_id = None

        greeting = ""  # Initialize as empty string
        jira_context = {}
        base_greeting = f"Hi {request.user.username}! "

        # Fetch Jira Context
        if jira_user_id:
            try:
                jira_user = jira_client.client.user(jira_user_id)
                jira_context['display_name'] = jira_user.displayName
                base_greeting = f"Hi {jira_context['display_name']}! "  # Use Jira display name

                issues = jira_client.get_user_issues(jira_user_id)
                jira_context['assigned_issues_count'] = len(issues)

                if len(issues) > 0:
                    recent_projects = list({issue['key'].split('-')[0] for issue in issues})[:3]
                    jira_context['recent_projects'] = recent_projects

            except JIRAError as e:
                logger.warning(f"Could not fetch Jira info for user {jira_user_id}: {e}")
            except Exception as e:
                logger.exception(f"An unexpected error occurred while fetching Jira data: {e}")

        # Construct the Prompt
        system_prompt = (
            "You are a helpful assistant designed to welcome users to a Jira integration. "
            "Your goal is to provide a personalized and engaging initial greeting, "
            "suggesting a few relevant actions the user can take within the Jira integration.\n\n"
            "**Context:**\n"
            f"- User's Django username: {request.user.username}\n"
        )
        if jira_context:
            system_prompt += f"- User's Jira display name: {jira_context.get('display_name', 'N/A')}\n"
            system_prompt += f"- Number of issues assigned to the user: {jira_context.get('assigned_issues_count', 0)}\n"
            if jira_context.get('recent_projects'):
                system_prompt += f"- User's recent projects: {', '.join(jira_context['recent_projects'])}\n"
        else:
            system_prompt += "- User is not linked to a Jira account.\n"

        system_prompt += (
            "\n**Instructions:**\n"
            "- Provide a short, friendly greeting.\n"
            "- Offer 2-3 specific suggestions of actions the user can take.\n"
            "- Tailor suggestions to the user's Jira context (if available).\n"
            "- If the user has no assigned issues or recent projects, suggest more general actions.\n"
            "- Format suggestions as a numbered list.\n"
            "- Keep the entire response concise (under 150 tokens).\n"
            "- Do *NOT* use function calls.  Respond only with plain text.\n\n"
            "**Examples of Good Suggestions:**\n"
            "- Check the status of your 3 open issues in Project ABC.\n"
            "- Add a comment to issue XYZ-123.\n"
            "- Update the status of your highest priority issue.\n"
            "- Search for users in your team.\n"
            "- View all available issue statuses.\n"
            "- Create a new issue in Project DEF."
        )

        user_prompt = "Welcome the user and provide suggestions."

        # Call OpenAI and Process Response
        try:
            response = openai_client.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150
            )
            openai_response = response.choices[0].message.content

            # Extract suggestions using regular expressions
            suggestions = re.findall(r"^\s*\d+\.\s*(.*?)\s*$", openai_response, re.MULTILINE)
            greeting = base_greeting + openai_response # Combine base greeting with suggestions


        except Exception as e:
            logger.error(f"Error generating greeting with OpenAI: {e}")
            suggestions = [  # Fallback suggestions (as a list)
                "Check the status of your assigned Jira issues.",
                "Add a comment to a Jira issue.",
                "Update the status of a Jira issue."
            ]
            greeting = base_greeting + "\n\nHere are a few things you can try:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions))


        # Create structured response
        response_data = {
            "type": "greeting",
            "message": greeting,
            "suggestions": suggestions
        }

        Conversation.objects.create(user=request.user, message=greeting, is_user_message=False)
        return Response(response_data, status=status.HTTP_200_OK)
