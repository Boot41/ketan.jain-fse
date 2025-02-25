from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, Conversation

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'jira_user_id')
    list_filter = ('user__is_staff',)
    search_fields = ('user__username', 'jira_user_id')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'is_user_message')
    list_filter = ('is_user_message', 'timestamp')
    search_fields = ('user__username', 'message')
    ordering = ('-timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
