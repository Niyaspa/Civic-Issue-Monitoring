import joblib
import os
import re
from django.conf import settings

_cat_model = None
_pri_model = None

def load_models():
    global _cat_model, _pri_model
    cat_path = os.path.join(settings.BASE_DIR, 'ml_engine', 'model.pkl')

    if os.path.exists(cat_path):
        try:
            _cat_model = joblib.load(cat_path)
        except Exception as e:
            print(f"Error loading category model: {e}")

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def predict_category(text):
    global _cat_model
    processed_text = preprocess_text(text)
    
    # Rule-based priority override for disasters
    disaster_keywords = ['flood', 'landslide', 'earthquake', 'tsunami', 'cyclone', 'fire', 'dam', 'cloud burst', 'storm']
    for kw in disaster_keywords:
        if kw in processed_text:
            return "DISASTER"

    if _cat_model is None:
        load_models()
    
    if _cat_model:
        try:
            return _cat_model.predict([processed_text])[0]
        except:
            return "OTHER"
    return "OTHER"

if __name__ == "__main__":
    import sys
    import django
    
    # Setup Django environment for standalone testing
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_monitor.settings')
    try:
        django.setup()
        load_models()
        
        test_text = "Huge pothole on the main road causing accidents"
        if len(sys.argv) > 1:
            test_text = " ".join(sys.argv[1:])
            
        print(f"Testing prediction for: '{test_text}'")
        category = predict_category(test_text)
        print(f"Predicted Category: {category}")
        
    except Exception as e:
        print(f"Failed to setup Django or test classifier: {e}")
