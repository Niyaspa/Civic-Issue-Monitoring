from django.db import models
from django.contrib.auth.models import User


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteerprofile')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    area = models.CharField(max_length=200, help_text="Area/locality where volunteer operates")
    is_available = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({'Available' if self.is_available else 'Unavailable'})"


class VolunteerResource(models.Model):
    RESOURCE_TYPES = [
        ('PERSONNEL', 'Personnel'),
        ('VEHICLE', 'Vehicle'),
        ('EQUIPMENT', 'Equipment'),
        ('MEDICAL', 'Medical Supplies'),
        ('FOOD', 'Food & Water'),
    ]

    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='resources')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    quantity = models.PositiveIntegerField()
    description = models.CharField(max_length=255, help_text="e.g. '3 rescue boats', '20 trained workers'")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.volunteer.name} - {self.get_resource_type_display()} x{self.quantity}"


class VolunteerAssignment(models.Model):
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('ACCEPTED', 'Accepted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DECLINED', 'Declined'),
    ]

    complaint = models.ForeignKey(
        'complaints.Complaint', on_delete=models.CASCADE, related_name='volunteer_assignments'
    )
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_made')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    notes = models.TextField(blank=True, help_text="Instructions from the official")
    volunteer_notes = models.TextField(blank=True, help_text="Updates from the volunteer")
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Assignment #{self.id}: {self.volunteer.name} → Complaint #{self.complaint.id}"
