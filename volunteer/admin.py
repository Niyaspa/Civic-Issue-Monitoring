from django.contrib import admin
from .models import VolunteerProfile, VolunteerResource, VolunteerAssignment

@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'area', 'is_available', 'registered_at']
    list_filter = ['is_available']
    search_fields = ['name', 'area']

@admin.register(VolunteerResource)
class VolunteerResourceAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'resource_type', 'quantity', 'description', 'updated_at']

@admin.register(VolunteerAssignment)
class VolunteerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'volunteer', 'complaint', 'status', 'assigned_by', 'assigned_at']
    list_filter = ['status']
