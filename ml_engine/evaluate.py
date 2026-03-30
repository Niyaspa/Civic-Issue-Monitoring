import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import os
import re

# Output directory for graphs
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metrics')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def clean(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def evaluate():
    # 1. Load CSV data
    data_path = os.path.join('ml_engine', 'data', 'complaints.csv')
    df_csv = pd.read_csv(data_path)
    df_csv = df_csv.dropna(subset=['text', 'category'])

    # 2. Load Database data (requires Django setup)
    import django
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_monitor.settings')
    try:
        django.setup()
        from complaints.models import Complaint
        db_data = Complaint.objects.all().values('description', 'category')
        df_db = pd.DataFrame(list(db_data))
        if not df_db.empty:
            df_db.columns = ['text', 'category']
            print(f"Loaded {len(df_db)} complaints from database for evaluation.")
        else:
            df_db = pd.DataFrame(columns=['text', 'category'])
    except Exception as e:
        print(f"Could not load database data: {e}")
        df_db = pd.DataFrame(columns=['text', 'category'])

    # Merge and clean
    df = pd.concat([df_csv, df_db], ignore_index=True)
    df = df.drop_duplicates(subset=['text'])
    df['text'] = df['text'].apply(clean)

    # 3. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['category'], test_size=0.2, random_state=42, stratify=df['category']
    )

    # 3. Create and Train Pipeline
    text_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', MultinomialNB()),
    ])
    text_clf.fit(X_train, y_train)

    # 4. Predict
    y_pred = text_clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2%}")

    # 5. Confusion Matrix Plot
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_test, y_pred, labels=text_clf.classes_)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=text_clf.classes_, yticklabels=text_clf.classes_)
    plt.title(f'Confusion Matrix (Overall Accuracy: {accuracy:.2%})')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    cm_path = os.path.join(OUTPUT_DIR, 'confusion_matrix.png')
    plt.savefig(cm_path)
    print(f"Saved confusion matrix to {cm_path}")
    plt.close()

    # 6. Classification Report (Metrics Plot)
    report = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).transpose().drop(['accuracy', 'macro avg', 'weighted avg'])
    
    report_df[['precision', 'recall', 'f1-score']].plot(kind='bar', figsize=(12, 6))
    plt.title('Performance Metrics by Category')
    plt.ylabel('Score')
    plt.xlabel('Category')
    plt.xticks(rotation=0)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    metrics_path = os.path.join(OUTPUT_DIR, 'metrics_chart.png')
    plt.savefig(metrics_path)
    print(f"Saved metrics chart to {metrics_path}")
    plt.close()

    # 7. Category Distribution
    plt.figure(figsize=(8, 6))
    df['category'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    plt.title('Dataset Category Distribution')
    plt.ylabel('')
    dist_path = os.path.join(OUTPUT_DIR, 'category_distribution.png')
    plt.savefig(dist_path)
    print(f"Saved distribution chart to {dist_path}")
    plt.close()

if __name__ == "__main__":
    evaluate()
