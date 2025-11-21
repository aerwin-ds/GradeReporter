# -----------------------------
# GradeReporter: Early Warning & Risk Prediction System
# Fully runnable in Google Colab
# -----------------------------

import pandas as pd # type: ignore
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore

# ---------------------------------------------
# 1. Create Sample Data (You can replace with CSV)
# ---------------------------------------------
data = {
    "StudentID": ["S001", "S002", "S003", "S004", "S005"],
    "Name": ["John", "Emily", "Carlos", "Aisha", "Fatima"],
    "Assignment1": [85, 92, 65, 45, 55],
    "Assignment2": [78, 88, 60, 40, 50],
    "Assignment3": [82, 91, 58, 42, 48],
    "Attendance": [0.92, 0.95, 0.78, 0.60, 0.65]   # values between 0–1
}

df = pd.DataFrame(data)

# ---------------------------------------------
# 2. Compute Final Grade
# (simple average of assignments)
# ---------------------------------------------
df["FinalGrade"] = df[["Assignment1", "Assignment2", "Assignment3"]].mean(axis=1)

# ---------------------------------------------
# 3. Risk Score Calculation
# Formula:
# risk = (100 - FinalGrade)*0.7 + (1 - Attendance)*100*0.3
# ---------------------------------------------
df["RiskScore"] = (100 - df["FinalGrade"]) * 0.7 + (1 - df["Attendance"]) * 100 * 0.3

# ---------------------------------------------
# 4. Assign Risk Level
# ---------------------------------------------
def classify_risk(score):
    if score < 30:
        return "Low"
    elif score < 60:
        return "Medium"
    else:
        return "High"

df["RiskLevel"] = df["RiskScore"].apply(classify_risk)

# ---------------------------------------------
# 5. Show Risk Dashboard
# ---------------------------------------------
print("\n📌 Student Risk Dashboard\n")
display(df[["StudentID", "Name", "FinalGrade", "Attendance", "RiskScore", "RiskLevel"]]) # type: ignore

# ---------------------------------------------
# 6. Grade Trend Visualization (optional)
# ---------------------------------------------
plt.figure(figsize=(10, 6))

for i in range(len(df)):
    student = df.iloc[i]
    grades = [student["Assignment1"], student["Assignment2"], student["Assignment3"]]
    plt.plot(["A1", "A2", "A3"], grades, marker='o', label=student["Name"])

plt.title("Student Grade Trends")
plt.xlabel("Assignments")
plt.ylabel("Grade")
plt.legend()
plt.grid(True)
plt.show()
