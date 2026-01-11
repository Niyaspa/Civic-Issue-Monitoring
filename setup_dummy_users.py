import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_monitor.settings')
django.setup()

from django.contrib.auth.models import User
from complaints.models import Department, OfficialProfile

def create_users():
    print("Starting dummy user creation...")
    
    password = 'User@123'
    
    users_data = [
        ('pwd_officer', 'Public Works Department (PWD)', False),
        ('social_officer', 'Social Justice Department', False),
        ('disaster_officer', 'Kerala State Disaster Management Authority (KSDMA)', False),
        ('general_officer', 'General Administration', False),
        ('admin', None, True),
    ]

    for username, dept_name, is_su in users_data:
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = is_su
        user.save()
        
        status = "Created" if created else "Updated"
        print(f"{status} user: {username}")
        
        if dept_name:
            try:
                dept = Department.objects.get(name=dept_name)
                # Link to profile
                OfficialProfile.objects.update_or_create(
                    user=user,
                    defaults={'department': dept}
                )
                print(f"  - Linked to {dept_name}")
            except Department.DoesNotExist:
                print(f"  - Error: Department '{dept_name}' not found")

    print("\nAll users created/updated with password: " + password)

if __name__ == "__main__":
    create_users()
