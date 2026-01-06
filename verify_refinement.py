import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_monitor.settings')
django.setup()

from complaints.models import Complaint

def verify_refinement():
    print("--- VERIFICATION START ---")
    
    test_cases = [
        ("Huge pothole on the main highway causing traffic jams", "ROAD"),
        ("Children begging at traffic signals", "SOCIAL"),
    ]

    for desc, expected in test_cases:
        c = Complaint(description=desc)
        c.save()
        
        status = "PASS" if c.category == expected else "FAIL"
        print(f"[{status}] Input: '{desc[:20]}...' -> Pred: {c.category}, Exp: {expected}")

    print("--- VERIFICATION END ---")
            
if __name__ == "__main__":
    verify_refinement()
