GradeReporter – Early Warning & Risk Prediction System
Status:Production Ready

Tech Stack

Python · Scikit-Learn · Streamlit UI · SQLite
Optional: Gemini AI for Insight Explanation

Overview

The Early Warning & Risk Prediction System identifies at-risk students by analyzing academic performance trends, missing assignments, behavior indicators, and historical grade patterns.
It generates a risk score, predicts final outcomes, and provides actionable interventions.

A Colab-ready notebook is included to train and evaluate the predictive model.

Features
Student Risk Analysis

Predicts risk of course failure or performance decline

Generates numerical Risk Score (0–100)

Flags high-risk students with alerts

Detects sudden drops in assignment completion

Machine Learning Model

Trained using Notebook/Colab (included)

Default model: Random Forest Classifier

Inputs: grades, trend slopes, attendance, missing work, assignment performance

Outputs: binary risk flag + probability score

Teacher & Admin Tools

Risk dashboard with per-student predictions

Filters: High Risk, Medium Risk, Low Risk

Suggested interventions based on risk type

Exportable risk reports

Optional AI Insights

If Gemini is enabled, the system also provides:

Human-readable explanations of predictions

Suggested intervention steps

Early-stage detection summaries

Architecture

Follows the standard GradeReporter three-layer structure:

Repository Layer (repository.py)

Retrieves student performance metrics

Prepares ML feature vectors

Stores/loads trained ML models

Provides historical and real-time data

Service Layer (service.py)

Loads ML model and generates predictions

Computes risk scores

Detects missing-assignment spikes

Generates optional AI explanations using Gemini

Handles caching and model fallback behavior

UI Layer (ui.py)

Teacher dashboard risk viewer

Student-level prediction details

Charts for risk probability + trend line

Intervention recommendation panel

Colab Notebook (colab_training.ipynb)

Loads dataset

Engineer features (grade trends, attendance, etc.)

Trains ML model

Exports model as .pkl file

Can be re-run anytime for retraining

Setup
1. Environment Variables

Add to your .env file:

FEATURE_EARLY_WARNING_SYSTEM=True
MODEL_PATH=./models/risk_model.pkl

# Optional AI explanations
GOOGLE_API_KEY=your-api-key-here
ENABLE_AI_RISK_INSIGHTS=True

2. Database Migration

Run:

python scripts/add_risk_predictions_table.py

Table Schema
CREATE TABLE RiskPredictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    prediction_date TEXT NOT NULL,
    model_version TEXT,
    explanation TEXT,
    FOREIGN KEY(student_id) REFERENCES Students(student_id)
);

3. Model Training (Colab)

Open and run the Colab notebook:

notebooks/early_warning_colab.ipynb


The notebook will:

Load training data

Train Random Forest Model

Evaluate model accuracy

Export risk_model.pkl

Place the exported model into:

/models/risk_model.pkl

Usage
Programmatic Example
from src.features.early_warning_system.service import RiskPredictor

predictor = RiskPredictor()

result = predictor.predict_student_risk(student_id=12)

print(result["risk_score"])
print(result["risk_level"])
print(result["explanation"])  # if AI enabled

Dashboard

Teachers can view:

Student list with risk levels

Detailed per-student predictions

Intervention suggestions

Trend charts and comparison metrics

Testing
source .venv/bin/activate
python scripts/test_early_warning.py

Test Coverage

Feature vector creation

ML model loading

Prediction generation

Risk score thresholds

AI explanation logic

Database storage behavior

Troubleshooting

“Model not found”

Ensure MODEL_PATH is correct

Make sure risk_model.pkl exists in /models/

“Predictions not showing”

Confirm FEATURE_EARLY_WARNING_SYSTEM=True

Validate Student has grade data

“AI explanation not generated”

Check GOOGLE_API_KEY

Enable ENABLE_AI_RISK_INSIGHTS=True

Future Enhancements

LSTM-based time-series prediction model

Behavior indicators (attendance, tardiness)

Automatic weekly risk summaries

Multi-model ensemble voting

Parent-facing risk summaries

File Structure
src/features/early_warning_system/
├── __init__.py
├── repository.py
├── service.py
├── ui.py
├── model_utils.py
├── README.md
models/
├── risk_model.pkl
notebooks/
├── early_warning_colab.ipynb
scripts/
├── add_risk_predictions_table.py
└── test_early_warning.py