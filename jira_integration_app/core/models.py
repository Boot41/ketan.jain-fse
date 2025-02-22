from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    jira_user_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}\'s profile'

# Signal to automatically create/update UserProfile when User is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_user_message = models.BooleanField()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp'])
        ]

    def __str__(self):
        return f'{"User" if self.is_user_message else "AI"} message at {self.timestamp}'


class ScrumUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scrum_updates')
    date = models.DateField(db_index=True)
    updates = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        # Ensure only one update per user per day
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date'])
        ]

    def __str__(self):
        return f'Scrum update by {self.user.username} on {self.date}'
