from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Feedback

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_travel_preferences', 'get_is_verified')
    list_filter = ('is_staff', 'is_superuser', 'profile__travel_preferences', 'profile__is_verified')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_travel_preferences(self, obj):
        return obj.profile.get_travel_preferences_display() if hasattr(obj, 'profile') else ''
    get_travel_preferences.short_description = 'Travel Preferences'
    
    def get_is_verified(self, obj):
        return obj.profile.is_verified if hasattr(obj, 'profile') else False
    get_is_verified.short_description = 'Verified'
    get_is_verified.boolean = True

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'rating', 'status', 'created_at')
    list_filter = ('rating', 'status', 'created_at')
    search_fields = ('subject', 'message', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'subject', 'message', 'rating')}),
        ('Status', {'fields': ('status',)}),
        ('Response', {'fields': ('admin_response', 'response_date')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
