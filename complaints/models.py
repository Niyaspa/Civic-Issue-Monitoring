from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(default='support@kerala.gov.in')
    
    def __str__(self):
        return self.name

class OfficialProfile(models.Model):
    from django.contrib.auth.models import User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} ({self.department.name})"

class Complaint(models.Model):
    from django.contrib.auth.models import User
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_complaints')
    CATEGORY_CHOICES = [
        ('DISASTER', 'Disaster & Climate Issues'),
        ('ROAD', 'Road & Transportation Safety'),
        ('SOCIAL', 'Poverty & Social Support'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()

    location = models.CharField(max_length=255, help_text="Address or visual description")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='complaints/', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Feedback fields
    rating = models.IntegerField(null=True, blank=True, help_text="Rating from 1 to 5")
    feedback_text = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False, help_text="Checked by a human official")

    @property
    def resolution_time_str(self):
        if not self.resolved_at:
            return None
        diff = self.resolved_at - self.created_at
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if days == 0 and hours == 0 and minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        elif days == 0 and hours == 0 and minutes == 0:
            parts.append("Less than a minute")
            
        return " ".join(parts)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = getattr(self, 'status', None)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        status_changed = not is_new and self.status != getattr(self, '_original_status', None)
        
        if status_changed and self.status == 'RESOLVED' and not self.resolved_at:
            from django.utils import timezone
            self.resolved_at = timezone.now()
            
        # 1. AI Classification (only if not verified and no category or OTHER)
        if not self.is_verified:
            from ml_engine.classifier import predict_category
            if not self.category or self.category == 'OTHER':
                self.category = predict_category(self.description)
            
        # 2. Assign Department based on Category
        # If is_verified, we should allow the human to change the category and update the department accordingly
        # But we only update department if it wasn't manually set to something else already?
        # Let's check mapping
        mapping = {
            'ROAD': 'Public Works Department (PWD)',
            'SOCIAL': 'Social Justice Department',
            'DISASTER': 'Kerala State Disaster Management Authority (KSDMA)',
        }
        
        # If it's new or the category was changed, update department automatically to match
        # unless it was already set explicitly.
        if is_new or self.is_verified:
            dep_name = mapping.get(self.category, 'General Administration')
            try:
                self.department = Department.objects.get(name=dep_name)
            except Department.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)
        
        # 3. Trigger Email Alert (only for new complaints)
        if is_new and self.department:
            self.send_alert_email()

        if is_new and self.reporter and getattr(self.reporter, 'email', None):
            self.send_confirmation_email()
        elif status_changed and self.reporter and getattr(self.reporter, 'email', None):
            self.send_status_update_email()
            
        self._original_status = self.status

    def send_alert_email(self):
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"NEW COMPLAINT: {self.get_category_display()} - Ticket #{self.id}"
        message = f"""
Dear Department Manager,

A new civic complaint has been registered and routed to your department via the CivicMonitor AI engine.

Category: {self.get_category_display()}
Description: {self.description}
Location: {self.location}
Reported At: {self.created_at}

Please log in to the dashboard to review and assign an official.

Best Regards,
CivicMonitor AI Team
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.department.email],
                fail_silently=False,
            )
            print(f"Alert sent to {self.department.email}")
        except Exception as e:
            print(f"Failed to send alert: {e}")

    def send_confirmation_email(self):
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"Complaint Registered: {self.get_category_display()} - Ticket #{self.id}"
        message = f"""
Dear {self.reporter.first_name or self.reporter.username},

Your complaint has been successfully registered. 

Category: {self.get_category_display()}
Description: {self.description}
Status: {self.get_status_display()}

It has been assigned to: {self.department.name if self.department else 'Pending Assignment'}

You will be notified when the status of your complaint changes.

Best Regards,
CivicMonitor AI Team
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.reporter.email],
                fail_silently=False,
            )
            print(f"Confirmation sent to {self.reporter.email}")
        except Exception as e:
            print(f"Failed to send confirmation: {e}")

    def send_status_update_email(self):
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"Complaint Status Updated: Ticket #{self.id}"
        message = f"""
Dear {self.reporter.first_name or self.reporter.username},

The status of your complaint regarding {self.get_category_display()} has been updated.

New Status: {self.get_status_display()}

Keep checking your dashboard for further updates.

Best Regards,
CivicMonitor AI Team
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.reporter.email],
                fail_silently=False,
            )
            print(f"Status update sent to {self.reporter.email}")
        except Exception as e:
            print(f"Failed to send status update: {e}")

    def __str__(self):
        return f"{self.get_category_display()} - {self.created_at.strftime('%Y-%m-%d')}"

