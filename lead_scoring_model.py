"""
ML Lead Scoring Model
Predicts lead close probability using historical sales data
Built by: Melina (Loyola University Chicago - Quinlan School of Business)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
import joblib

# Load data
print("="*60)
print("ML LEAD SCORING MODEL - TRAINING & EVALUATION")
print("="*60)

df = pd.read_csv('lead_scoring_dataset.csv')
print(f"\nLoaded {len(df)} historical leads")
print(f"Win Rate: {(df['Outcome']=='Won').mean()*100:.1f}%\n")

# Prepare features for ML
df_ml = df.copy()

# Encode categorical variables
label_encoders = {}
categorical_cols = ['Industry', 'Company_Size', 'Lead_Source', 'Budget_Range', 
                   'Decision_Timeline', 'Job_Title', 'Region']

for col in categorical_cols:
    le = LabelEncoder()
    df_ml[col + '_encoded'] = le.fit_transform(df_ml[col])
    label_encoders[col] = le

# Select features for model
feature_cols = [
    'Industry_encoded', 'Company_Size_encoded', 'Employee_Count',
    'Lead_Source_encoded', 'Budget_Range_encoded', 'Decision_Timeline_encoded',
    'Job_Title_encoded', 'Region_encoded', 'Email_Opens', 'Email_Clicks',
    'Website_Visits', 'Pricing_Page_Views', 'Demo_Requested', 'Response_Time_Hours'
]

X = df_ml[feature_cols]
y = (df_ml['Outcome'] == 'Won').astype(int)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training set: {len(X_train)} leads")
print(f"Test set: {len(X_test)} leads\n")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Logistic Regression
print("Training Logistic Regression Model...")
log_model = LogisticRegression(random_state=42, max_iter=1000)
log_model.fit(X_train_scaled, y_train)

# Train Random Forest for comparison
print("Training Random Forest Model...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
rf_model.fit(X_train_scaled, y_train)

# Evaluate both models
print("\n" + "="*60)
print("MODEL PERFORMANCE COMPARISON")
print("="*60)

for name, model in [("Logistic Regression", log_model), ("Random Forest", rf_model)]:
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    print(f"\n{name}:")
    print(f"  Accuracy:  {accuracy_score(y_test, y_pred):.3f}")
    print(f"  Precision: {precision_score(y_test, y_pred):.3f}")
    print(f"  Recall:    {recall_score(y_test, y_pred):.3f}")
    print(f"  F1 Score:  {f1_score(y_test, y_pred):.3f}")
    print(f"  ROC AUC:   {roc_auc_score(y_test, y_pred_proba):.3f}")

# Use Logistic Regression as primary model (more interpretable)
final_model = log_model
y_pred = final_model.predict(X_test_scaled)
y_pred_proba = final_model.predict_proba(X_test_scaled)[:, 1]

# Confusion Matrix
print("\n" + "="*60)
print("CONFUSION MATRIX")
print("="*60)
cm = confusion_matrix(y_test, y_pred)
print(f"\n                Predicted")
print(f"               Lost   Won")
print(f"Actual Lost     {cm[0,0]:3d}   {cm[0,1]:3d}")
print(f"       Won      {cm[1,0]:3d}   {cm[1,1]:3d}")

print(f"\nTrue Negatives:  {cm[0,0]} (correctly predicted Lost)")
print(f"False Positives: {cm[0,1]} (predicted Won, actually Lost)")
print(f"False Negatives: {cm[1,0]} (predicted Lost, actually Won)")
print(f"True Positives:  {cm[1,1]} (correctly predicted Won)")

# Feature Importance
print("\n" + "="*60)
print("TOP 10 MOST IMPORTANT FEATURES")
print("="*60)

feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Coefficient': abs(final_model.coef_[0])
}).sort_values('Coefficient', ascending=False).head(10)

print(f"\n{'Feature':<30} {'Importance':<10}")
print("-"*40)
for _, row in feature_importance.iterrows():
    feature_name = row['Feature'].replace('_encoded', '')
    print(f"{feature_name:<30} {row['Coefficient']:.4f}")

# Save model and preprocessing objects
print("\n" + "="*60)
print("SAVING MODEL")
print("="*60)
joblib.dump(final_model, 'lead_scoring_model.pkl')
joblib.dump(scaler, 'lead_scoring_scaler.pkl')
joblib.dump(label_encoders, 'lead_scoring_encoders.pkl')
joblib.dump(feature_cols, 'feature_columns.pkl')

print("\nModel artifacts saved:")
print("  - lead_scoring_model.pkl")
print("  - lead_scoring_scaler.pkl")
print("  - lead_scoring_encoders.pkl")
print("  - feature_columns.pkl")

print("\n" + "="*60)
print("MODEL TRAINING COMPLETE!")
print("="*60)
print(f"\nFinal Model Accuracy: {accuracy_score(y_test, y_pred)*100:.1f}%")
print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.3f}")
print("\nReady for deployment!")
