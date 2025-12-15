# File: train_nutrition_predictor_indb.py

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

print("=" * 80)
print("NUTRITION PREDICTOR TRAINING - INDB DATASET (MACRO-BASED)")
print("=" * 80)

# Load feature-engineered data
df = pd.read_csv("data/indb_features_with_targets.csv")
print(f"\n📊 Loaded dataset: {df.shape}")

# Separate features (X) and targets (y)
feature_cols = [
    col
    for col in df.columns
    if col not in ["recipe_code", "calories", "protein", "carbs", "fats", "sodium"]
]
X = df[feature_cols]

y_protein = df["protein"]  # grams
y_carbs = df["carbs"]      # grams
y_fats = df["fats"]        # grams

print(f"\n🔹 Features (X): {X.shape[1]} features")
print(f" {feature_cols}")

print("\n🔹 Targets (y): Predicting protein, carbs, fats (grams)")
print(f" Protein range: {y_protein.min():.2f} - {y_protein.max():.2f} g (mean {y_protein.mean():.2f})")
print(f" Carbs range:   {y_carbs.min():.2f} - {y_carbs.max():.2f} g (mean {y_carbs.mean():.2f})")
print(f" Fats range:    {y_fats.min():.2f} - {y_fats.max():.2f} g (mean {y_fats.mean():.2f})")

# Train-test split (80-20)
X_train, X_test, y_protein_train, y_protein_test, y_carbs_train, y_carbs_test, y_fats_train, y_fats_test = train_test_split(
    X, y_protein, y_carbs, y_fats, test_size=0.2, random_state=42
)

print("\n📊 Split:")
print(f" Train: {len(X_train)} recipes ({len(X_train)/len(X)*100:.1f}%)")
print(f" Test:  {len(X_test)} recipes ({len(X_test)/len(X)*100:.1f}%)")

# Scale features (same scaler for all three models)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

os.makedirs("models", exist_ok=True)
joblib.dump(scaler, "models/indb_scaler.pkl")
print("\n✓ Scaler saved: models/indb_scaler.pkl")

# Train models for each macro
def train_macro_model(name: str, y_train, y_test):
    print(f"\n[{name}] Training Gradient Boosting Regressor...")

    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )

    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f" ✓ RMSE: {rmse:.2f} g")
    print(f" ✓ MAE:  {mae:.2f} g")
    print(f" ✓ R²:   {r2:.4f}")

    return model, y_pred, {"RMSE": rmse, "MAE": mae, "R²": r2}

results = {}
predictions = {}

# Protein model
model_protein, y_protein_pred, metrics_protein = train_macro_model("Protein", y_protein_train, y_protein_test)
results["Protein"] = metrics_protein
predictions["Protein"] = (y_protein_test, y_protein_pred)

# Carbs model
model_carbs, y_carbs_pred, metrics_carbs = train_macro_model("Carbs", y_carbs_train, y_carbs_test)
results["Carbs"] = metrics_carbs
predictions["Carbs"] = (y_carbs_test, y_carbs_pred)

# Fats model
model_fats, y_fats_pred, metrics_fats = train_macro_model("Fats", y_fats_train, y_fats_test)
results["Fats"] = metrics_fats
predictions["Fats"] = (y_fats_test, y_fats_pred)

# Save models
print("\n💾 Saving macro models...")
joblib.dump(model_protein, "models/indb_protein.pkl")
print(" ✓ models/indb_protein.pkl")

joblib.dump(model_carbs, "models/indb_carbs.pkl")
print(" ✓ models/indb_carbs.pkl")

joblib.dump(model_fats, "models/indb_fats.pkl")
print(" ✓ models/indb_fats.pkl")

# Optional: save metrics summary
results_df = pd.DataFrame(results).T.reset_index().rename(columns={"index": "Macro"}).sort_values("MAE")
results_df.to_csv("models/indb_macro_model_comparison.csv", index=False)
print(" ✓ models/indb_macro_model_comparison.csv")

print("\n" + "=" * 80)
print("MODEL PERFORMANCE (MACROS)")
print("=" * 80)
print("\n" + results_df.to_string(index=False))

print("\n" + "=" * 80)
print("✅ TRAINING COMPLETE (MACRO-BASED)")
print("=" * 80)
print("\n📁 Models saved in: models/")
print("=" * 80)
