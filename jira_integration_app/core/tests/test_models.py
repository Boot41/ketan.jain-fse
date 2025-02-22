from django.test import TestCase
from django.contrib.auth.models import User
from core.models import UserProfile, Conversation
from django.utils import timezone

class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
    def test_profile_creation(self):
        """Test that a UserProfile is automatically created when a User is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
        
    def test_profile_str_representation(self):
        """Test the string representation of UserProfile"""
        expected_str = "testuser's profile"
        self.assertEqual(str(self.user.profile), expected_str)
        
    def test_jira_user_id_field(self):
        """Test that jira_user_id can be set and retrieved"""
        test_jira_id = "JIRA123"
        self.user.profile.jira_user_id = test_jira_id
        self.user.profile.save()
        
        # Refresh from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.jira_user_id, test_jira_id)

class ConversationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_conversation_creation(self):
        """Test creating a new conversation"""
        conv = Conversation.objects.create(
            user=self.user,
            message="Test message",
            is_user_message=True
        )
        
        self.assertEqual(conv.message, "Test message")
        self.assertTrue(conv.is_user_message)
        self.assertIsNotNone(conv.timestamp)
        
    def test_conversation_ordering(self):
        """Test that conversations are ordered by timestamp descending"""
        # Create conversations with different timestamps
        conv1 = Conversation.objects.create(
            user=self.user,
            message="First message",
            is_user_message=True
        )
        conv2 = Conversation.objects.create(
            user=self.user,
            message="Second message",
            is_user_message=False
        )
        
        conversations = Conversation.objects.filter(user=self.user)
        self.assertEqual(conversations[0], conv2)  # Most recent first
        self.assertEqual(conversations[1], conv1)
        
    def test_conversation_str_representation(self):
        """Test the string representation of Conversation"""
        conv = Conversation.objects.create(
            user=self.user,
            message="Test message",
            is_user_message=True
        )
        self.assertIn("User message at", str(conv))
