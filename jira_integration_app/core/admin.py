from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.html import format_html
from .models import UserProfile, Conversation, ScrumUpdate

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Jira Integration Profile'
    fields = ('jira_user_id',)

    def get_queryset(self, request):
        # Only show profiles for staff users
        return super().get_queryset(request).filter(user__is_staff=True)

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_jira_user_id')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__jira_user_id')

    def get_jira_user_id(self, obj):
        return obj.profile.jira_user_id if hasattr(obj, 'profile') else ''
    get_jira_user_id.short_description = 'Jira User ID'
    get_jira_user_id.admin_order_field = 'profile__jira_user_id'

    def get_queryset(self, request):
        # Include profile in queryset to avoid N+1 queries
        return super().get_queryset(request).select_related('profile')

    def get_inline_instances(self, request, obj=None):
        return super().get_inline_instances(request, obj)

# Register UserProfile model separately for direct access
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'jira_user_id', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'jira_user_id')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('user__is_staff',)

    def get_queryset(self, request):
        # Only show profiles for staff users
        return super().get_queryset(request).filter(user__is_staff=True)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'truncated_message', 'is_user_message', 'timestamp')
    list_filter = ('user', 'is_user_message', 'timestamp')
    search_fields = ('user__username', 'message')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def truncated_message(self, obj):
        if len(obj.message) > 100:
            return format_html('<span title="{}">{}</span>', 
                             obj.message, 
                             obj.message[:97] + '...')
        return obj.message
    truncated_message.short_description = 'Message'


@admin.register(ScrumUpdate)
class ScrumUpdateAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'truncated_updates', 'created_at')
    list_filter = ('user', 'date', 'created_at')
    search_fields = ('user__username', 'updates')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date', '-created_at')
    date_hierarchy = 'date'

    def truncated_updates(self, obj):
        if len(obj.updates) > 100:
            return format_html('<span title="{}">{}</span>', 
                             obj.updates, 
                             obj.updates[:97] + '...')
        return obj.updates
    truncated_updates.short_description = 'Updates'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Re-register UserAdmin and register UserProfileAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
