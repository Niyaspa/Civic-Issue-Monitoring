import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_monitor.settings')
django.setup()

from complaints.models import Complaint, Department

def verify_active_learning():
    print("--- VERIFYING ACTIVE LEARNING ---")
    
    # 1. Create a "thief" complaint (should go to SOCIAL but we'll pretend it's wrong)
    desc = "I saw a suspicious person trying to open car doors in the parking lot."
    c = Complaint.objects.create(description=desc, location="Central Parking")
    
    print(f"Created Complaint: '{desc}'")
    print(f"Initial Category (AI): {c.category}")
    print(f"Initial Verification Status: {c.is_verified}")
    print(f"Initial Department: {c.department}")

    # 2. Simulate manual correction to ROAD (just for testing logic)
    print("\n--- Simulating Manual Correction to ROAD ---")
    c.category = 'ROAD'
    c.is_verified = True
    c.save()
    
    # Reload from DB
    c.refresh_from_db()
    print(f"Updated Category: {c.category}")
    print(f"Updated Verification Status: {c.is_verified}")
    print(f"Updated Department: {c.department}")

    # 3. Check if re-training counts it
    print("\n--- Checking Re-training Data Integration ---")
    from ml_engine.train import train_model
    # This should print cleaning logs or merge logs
    train_model()
    
    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_active_learning()
