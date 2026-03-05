import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os
import re
from django.conf import settings

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

def train_model(algorithm='nb'):
    """
    Trains models for category using specified algorithm.
    algorithm: 'nb' (Naive Bayes), 'lr' (Logistic Regression), 'rf' (Random Forest)
    """
    # Paths
    data_path = os.path.join(settings.BASE_DIR, 'ml_engine', 'data', 'complaints.csv')
    cat_model_path = os.path.join(settings.BASE_DIR, 'ml_engine', 'model.pkl') # Keep existing name for backward compatibility

    # Load CSV data
    try:
        df = pd.read_csv(data_path, encoding='utf-8')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Load Database data
    try:
        from complaints.models import Complaint
        db_complaints = Complaint.objects.all().values('description', 'category')
        if db_complaints.exists():
            df_db = pd.DataFrame(list(db_complaints))
            df_db.columns = ['text', 'category']
            df = pd.concat([df, df_db], ignore_index=True)
    except Exception as e:
        print(f"Database data not available: {e}")

    # Clean data
    df = df.dropna(subset=['text', 'category'])
    df = df.drop_duplicates(subset=['text'])

    def clean_text(text):
        text = str(text).lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    df['text'] = df['text'].apply(clean_text)

    # Choose classifier
    if algorithm == 'lr':
        clf = LogisticRegression(max_iter=1000)
    elif algorithm == 'rf':
        clf = RandomForestClassifier(n_estimators=100)
    else:
        clf = MultinomialNB()

    # Pipeline helper
    def create_pipeline(classifier):
        return Pipeline([
            ('vect', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', classifier),
        ])

    # Train Category Model
    print(f"Training Category model using {algorithm}...")
    cat_pipe = create_pipeline(clf)
    cat_pipe.fit(df['text'], df['category'])
    joblib.dump(cat_pipe, cat_model_path)
    
    print(f"Success: Category model trained and saved.")

if __name__ == "__main__":
    import sys
    import django
    
    # 1. Setup Django environment for standalone execution
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_monitor.settings')
    try:
        django.setup()
        print("Django setup successful for standalone run.")
        train_model()
    except Exception as e:
        print(f"Failed to setup Django or train model: {e}")
        print("\nTIP: Make sure you are running this from the project root or have your virtual environment activated.")
