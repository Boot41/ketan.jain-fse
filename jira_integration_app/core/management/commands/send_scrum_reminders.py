"""
Management command to send scrum update reminders to users.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from core.notifications import NotificationManager


class Command(BaseCommand):
    help = 'Send scrum update reminders to users who have not submitted their updates'

    def handle(self, *args, **options):
        """
        Execute the command to send scrum update reminders.
        """
        now = timezone.now()
        target_hour = settings.SCRUM_UPDATE_REMINDER_HOUR
        target_minute = settings.SCRUM_UPDATE_REMINDER_MINUTE
        
        # Only send reminders if it's the target time
        if now.hour == target_hour and now.minute == target_minute:
            NotificationManager.check_missing_updates()
            self.stdout.write(
                self.style.SUCCESS('Successfully sent scrum update reminders')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Not the target time for sending reminders')
            )
