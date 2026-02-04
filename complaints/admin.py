from django.contrib import admin
from .models import Complaint, Department, OfficialProfile

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'status', 'created_at', 'is_verified')
    list_filter = ('category', 'status', 'is_verified')
    search_fields = ('description', 'location')

admin.site.register(Department)
admin.site.register(OfficialProfile)
