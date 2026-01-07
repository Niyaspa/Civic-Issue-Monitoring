import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_monitor.settings')
django.setup()

from complaints.models import Complaint
from django.test import RequestFactory
from dashboard.views import complaint_data
import json

def verify():
    print("Verifying Civic Issue System...")

    # 1. Test ML Routing
    print("\n1. Testing ML Routing...")
    desc = "There is a massive flood in the downtown area, people are stuck."
    # Create complaint manually to trigger save method
    c = Complaint(description=desc, location="Downtown", latitude=10.0, longitude=20.0)
    c.save()
    
    print(f"Input: {desc}")
    print(f"Predicted Category: {c.category}")
    
    if c.category == 'DISASTER':
        print("SUCCESS: Routing works!")
    else:
        print(f"FAILURE: Expected DISASTER, got {c.category}")

    # 2. Test Dashboard API
    print("\n2. Testing Dashboard API...")
    from django.contrib.auth.models import User
    
    # Create a test superuser if it doesn't exist
    test_user, created = User.objects.get_or_create(username='testadmin', defaults={'is_superuser': True, 'is_staff': True})
    if not created:
        test_user.is_superuser = True
        test_user.is_staff = True
        test_user.save()

    factory = RequestFactory()
    request = factory.get('/dashboard/api/complaints/')
    request.user = test_user
    
    response = complaint_data(request)
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"API Returned {len(data.get('complaints', []))} complaints.")
        found = False
        for item in data.get('complaints', []):
            if item['description'].startswith(desc[:20]):
                found = True
                break
        
        if found:
            print("SUCCESS: Complaint found in Dashboard API.")
        else:
            print("FAILURE: Complaint not found in API.")
    else:
        print(f"FAILURE: API returned status {response.status_code}")

    # Cleanup
    c.delete()
    if created:
        test_user.delete()
    print("\nCleanup complete.")

if __name__ == "__main__":
    try:
        verify()
    except Exception:
        import traceback
        traceback.print_exc()
