"""
Notification handling for the Jira Integration App.
"""
from typing import Dict, Any, Optional, List
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import ScrumUpdate


class NotificationManager:
    """Manages notifications for the application."""
    
    @staticmethod
    def notify_missing_scrum_update(user: User) -> None:
        """
        Notify user about missing scrum update for the day.
        
        Args:
            user: The user to notify
        """
        if not user.email:
            return
            
        subject = "Daily Scrum Update Reminder"
        message = (
            f"Hi {user.get_full_name() or user.username},\n\n"
            f"You haven't submitted your scrum update for today. "
            f"Please take a moment to update your team on your progress.\n\n"
            f"Best regards,\nYour JiraBot"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
    
    @staticmethod
    def notify_jira_sync_error(user: User, issue_keys: List[str], error_message: str) -> None:
        """
        Notify user about Jira synchronization errors.
        
        Args:
            user: The user to notify
            issue_keys: List of Jira issue keys that failed to sync
            error_message: The error message
        """
        if not user.email:
            return
            
        subject = "Jira Sync Error"
        message = (
            f"Hi {user.get_full_name() or user.username},\n\n"
            f"There was an error syncing your scrum update with the following Jira issues:\n"
            f"{', '.join(issue_keys)}\n\n"
            f"Error: {error_message}\n\n"
            f"Please check your Jira access and try again.\n\n"
            f"Best regards,\nYour JiraBot"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
    
    @staticmethod
    def check_missing_updates() -> None:
        """
        Check for users who haven't submitted their scrum update today
        and send them a reminder.
        """
        today = timezone.now().date()
        
        # Get all users who should submit updates
        all_users = User.objects.filter(is_active=True)
        
        # Get users who have submitted updates today
        updated_users = ScrumUpdate.objects.filter(
            date=today
        ).values_list('user_id', flat=True)
        
        # Find users who haven't submitted updates
        missing_users = all_users.exclude(id__in=updated_users)
        
        # Send notifications
        for user in missing_users:
            NotificationManager.notify_missing_scrum_update(user)
