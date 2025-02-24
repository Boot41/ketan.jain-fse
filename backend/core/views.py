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
            # Get user message from request
            user_message = request.data.get('message')
            if not user_message:
                return Response({'error': 'Message is required'}, 
                               status=status.HTTP_400_BAD_REQUEST)

            # Get user profile
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return Response({'error': 'User profile not found'}, 
                               status=status.HTTP_404_NOT_FOUND)

            # Save user message to conversation history
            Conversation.objects.create(
                user=request.user,
                message=user_message,
                is_user_message=True
            )

            # Get conversation history (last 10 messages)
            conversation_history = [
                {
                    'role': 'user' if msg.is_user_message else 'assistant',
                    'content': msg.message
                }
                for msg in Conversation.objects.filter(user=request.user)
                .order_by('-timestamp')[:10][::-1]
            ]

            # Initialize OpenAI and Jira clients
            openai_client = OpenAIClient()
            jira_client = JiraClient()

            # Get intent and parameters from OpenAI
            result = openai_client.get_intent_and_parameters(user_message, conversation_history)

            # Handle function calls or text response
            if 'function_name' in result:
                # Map function names to Jira client methods
                jira_functions = {
                    'get_user_issues': jira_client.get_user_issues,
                    'add_comment_to_issue': jira_client.add_comment_to_issue,
                    'update_issue_status': jira_client.update_issue_status,
                    'create_issue': jira_client.create_issue,
                    'get_all_statuses': jira_client.get_all_statuses,
                    'search_users': jira_client.search_users
                }

                # Get the appropriate function
                jira_function = jira_functions.get(result['function_name'])
                if not jira_function:
                    raise ValueError(f"Unknown function: {result['function_name']}")

                # For get_user_issues, use the Jira user ID from UserProfile
                if result['function_name'] == 'get_user_issues':
                    if not user_profile.jira_user_id:
                        raise ValueError("Jira user ID not set in your profile")
                    result['arguments']['jira_user_id'] = user_profile.jira_user_id

                # Execute the Jira function with provided arguments
                jira_response = jira_function(**result['arguments'])

                # Construct response message based on the function called
                response_message = f"Successfully executed {result['function_name']}: {jira_response}"
            else:
                # Use the text response directly
                response_message = result['response']

            # Save AI response to conversation history
            Conversation.objects.create(
                user=request.user,
                message=response_message,
                is_user_message=False
            )

            return Response({'message': response_message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InitialGreetingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        greeting = f"Hi {request.user.username}! Here are the top 3 things I can help you with today:\n\n"
        greeting += "1. Update the status of your Jira tickets.\n"
        greeting += "2. Get a summary of your assigned tickets.\n"
        greeting += "3. Add comments to your tickets.\n\n"
        greeting += "What would you like to do?"

        # Save greeting to conversation history
        Conversation.objects.create(
            user=request.user,
            message=greeting,
            is_user_message=False
        )

        return Response({'message': greeting}, status=status.HTTP_200_OK)
