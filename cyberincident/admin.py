from django.contrib import admin
from .models import Profile, Incident, Evidence, ResponseAction

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'status', 'priority', 'reporter', 'reported_at']
    list_filter = ['category', 'status', 'priority', 'reported_at']
    search_fields = ['title', 'description']
    readonly_fields = ['reported_at', 'updated_at']
    date_hierarchy = 'reported_at'

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'incident', 'uploaded_by', 'uploaded_at', 'is_verified']
    list_filter = ['is_verified', 'uploaded_at']
    search_fields = ['file_name', 'description']

@admin.register(ResponseAction)
class ResponseActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'incident', 'action_type', 'performer', 'timestamp', 'is_completed']
    list_filter = ['action_type', 'is_completed', 'timestamp']
    search_fields = ['action_text']