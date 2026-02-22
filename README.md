# CivicMonitor AI: Civic Issue Monitoring & Management System

CivicMonitor is an AI-powered platform designed to streamline the reporting, classification, and resolution of civic issues (e.g., road damage, social welfare needs, disaster alerts). It uses Machine Learning to automatically route complaints to the appropriate government departments.

---

## 🚀 Project Overview

Everything we've accomplished so far:
1.  **Environment Setup**: Configured a Python virtual environment (`.venv`) and resolved package import issues.
2.  **User Authentication**: Implemented a login system with distinct roles (Admins vs. Departmental Officials).
3.  **Departmental Routing**: Created a system where complaints are automatically assigned to specific departments based on their content.
4.  **AI Classification**: Integrated a Machine Learning engine to predict issue categories from text descriptions.
5.  **Interactive Dashboard**: Built a frontend dashboard with live map data (Leaflet.js) and analytical charts (Chart.js).
6.  **Active Learning**: Implemented a feedback loop where officials can correct AI predictions, improving the model over time.

---

## 📂 Project Structure & Files

### 🏛️ Core Project
- `manage.py`: Django's command-line utility for administrative tasks.
- `civic_monitor/`: Main configuration and global templates.
- `complaints/`: Core logic for reporting and stores the `is_verified` feedback.
- `dashboard/`: Operational UI for officials and analytical views.
- `ml_engine/`: The Machine Learning powerhouse (Classifier, Trainer, and Evaluator).

---

## 🧠 Machine Learning Implementation

The system uses a **Hybrid Classifier** approach to ensure high accuracy for critical civic issues.

### 1. Classification Method
The engine uses a combination of **Heuristic Rules** and **Probabilistic Modeling**:
- **Rule-Based (Step 1)**: The text is scanned for high-priority keywords (e.g., "flood", "stolen", "pothole"). If a critical match is found, it is routed immediately.
- **Multinomial Naive Bayes (Step 2)**: If keywords aren't conclusive, the text is passed to a Naive Bayes model. This algorithm calculates the probability of a category based on word frequencies.

### 2. Training Data & Active Learning
The system employs an **Active Learning** loop to improve over time:
- **Base Data**: 150+ categorized examples in `ml_engine/data/complaints.csv`.
- **Live Feedback**: Complaints submitted through the app are stored in the database. When an official corrects a category in the dashboard, it is marked as **Verified**.
- **Data Merging**: The training script automatically merges the base CSV data with live database records, prioritizing human-verified data to "teach" the model.

### 3. Operational Metrics
- **Current Accuracy**: **81.4%** across categories (ROAD, SOCIAL, DISASTER, OTHER).
- **Evaluation**: Use `ml_engine/evaluate.py` to generate performance charts. Graphs are automatically saved to `ml_engine/metrics/`.

---

## 🛠️ How to Run
1.  **Activate Environment**: `.\.venv\Scripts\activate`
2.  **Train Model**: `python ml_engine/train.py` (Run this to include new database entries).
3.  **Evaluate Performance**: `python ml_engine/evaluate.py` (Generates graphs in `ml_engine/metrics/`).
4.  **Run Server**: `python manage.py runserver`
5.  **Access App**: Open `http://127.0.0.1:8000/`.

**Admin Credentials:**
- Username: `admin`
- Password: `User@123`
