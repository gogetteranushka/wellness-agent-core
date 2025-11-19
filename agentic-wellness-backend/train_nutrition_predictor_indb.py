# File: train_nutrition_predictor_indb.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

print("="*80)
print("NUTRITION PREDICTOR TRAINING - INDB DATASET")
print("="*80)

# Load feature-engineered data
df = pd.read_csv('data/indb_features_with_targets.csv')
print(f"\n📊 Loaded dataset: {df.shape}")

# Separate features (X) and targets (y)
feature_cols = [col for col in df.columns if col not in ['recipe_code', 'calories', 'protein', 'carbs', 'fats', 'sodium']]
X = df[feature_cols]
y_calories = df['calories']

print(f"\n🔹 Features (X): {X.shape[1]} features")
print(f"   {feature_cols}")
print(f"\n🔹 Target (y): Predicting calories")
print(f"   Range: {y_calories.min():.2f} - {y_calories.max():.2f} kcal")
print(f"   Mean: {y_calories.mean():.2f} kcal")
print(f"   Std Dev: {y_calories.std():.2f} kcal")

# Train-test split (80-20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_calories, test_size=0.2, random_state=42
)

print(f"\n📊 Split:")
print(f"   Train: {len(X_train)} recipes ({len(X_train)/len(X)*100:.1f}%)")
print(f"   Test: {len(X_test)} recipes ({len(X_test)/len(X)*100:.1f}%)")

# Scale features (important for Neural Network)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save scaler
os.makedirs('models', exist_ok=True)
joblib.dump(scaler, 'models/indb_scaler.pkl')
print("\n✓ Scaler saved: models/indb_scaler.pkl")

print("\n" + "="*80)
print("TRAINING MODELS")
print("="*80)

models = {}
results = []
predictions = {}

# Model 1: Linear Regression
print("\n[1/4] Training Linear Regression...")
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)

rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
mae_lr = mean_absolute_error(y_test, y_pred_lr)
r2_lr = r2_score(y_test, y_pred_lr)

models['Linear Regression'] = lr
predictions['Linear Regression'] = y_pred_lr
results.append({
    'Model': 'Linear Regression',
    'RMSE': rmse_lr,
    'MAE': mae_lr,
    'R²': r2_lr
})

print(f"✓ RMSE: {rmse_lr:.2f} kcal")
print(f"✓ MAE: {mae_lr:.2f} kcal")
print(f"✓ R²: {r2_lr:.4f}")

# Model 2: Random Forest
print("\n[2/4] Training Random Forest...")
rf = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
mae_rf = mean_absolute_error(y_test, y_pred_rf)
r2_rf = r2_score(y_test, y_pred_rf)

models['Random Forest'] = rf
predictions['Random Forest'] = y_pred_rf
results.append({
    'Model': 'Random Forest',
    'RMSE': rmse_rf,
    'MAE': mae_rf,
    'R²': r2_rf
})

print(f"✓ RMSE: {rmse_rf:.2f} kcal")
print(f"✓ MAE: {mae_rf:.2f} kcal")
print(f"✓ R²: {r2_rf:.4f}")

# Model 3: Gradient Boosting
print("\n[3/4] Training Gradient Boosting...")
gb = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
gb.fit(X_train, y_train)
y_pred_gb = gb.predict(X_test)

rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
mae_gb = mean_absolute_error(y_test, y_pred_gb)
r2_gb = r2_score(y_test, y_pred_gb)

models['Gradient Boosting'] = gb
predictions['Gradient Boosting'] = y_pred_gb
results.append({
    'Model': 'Gradient Boosting',
    'RMSE': rmse_gb,
    'MAE': mae_gb,
    'R²': r2_gb
})

print(f"✓ RMSE: {rmse_gb:.2f} kcal")
print(f"✓ MAE: {mae_gb:.2f} kcal")
print(f"✓ R²: {r2_gb:.4f}")

# Model 4: Neural Network
print("\n[4/4] Training Neural Network...")
nn = MLPRegressor(
    hidden_layer_sizes=(100, 50),
    activation='relu',
    solver='adam',
    max_iter=500,
    random_state=42
)
nn.fit(X_train_scaled, y_train)
y_pred_nn = nn.predict(X_test_scaled)

rmse_nn = np.sqrt(mean_squared_error(y_test, y_pred_nn))
mae_nn = mean_absolute_error(y_test, y_pred_nn)
r2_nn = r2_score(y_test, y_pred_nn)

models['Neural Network'] = nn
predictions['Neural Network'] = y_pred_nn
results.append({
    'Model': 'Neural Network',
    'RMSE': rmse_nn,
    'MAE': mae_nn,
    'R²': r2_nn
})

print(f"✓ RMSE: {rmse_nn:.2f} kcal")
print(f"✓ MAE: {mae_nn:.2f} kcal")
print(f"✓ R²: {r2_nn:.4f}")

# Model Comparison
print("\n" + "="*80)
print("MODEL COMPARISON")
print("="*80)

results_df = pd.DataFrame(results).sort_values('MAE')
print("\n" + results_df.to_string(index=False))

best_model_name = results_df.iloc[0]['Model']
best_model = models[best_model_name]

print(f"\n🏆 BEST MODEL: {best_model_name}")
print(f"   MAE: {results_df.iloc[0]['MAE']:.2f} kcal")
print(f"   RMSE: {results_df.iloc[0]['RMSE']:.2f} kcal")
print(f"   R²: {results_df.iloc[0]['R²']:.4f}")

# Save models
print("\n💾 Saving models...")
for name, model in models.items():
    filename = f"models/indb_{name.lower().replace(' ', '_')}.pkl"
    joblib.dump(model, filename)
    print(f"   ✓ {filename}")

joblib.dump(best_model, 'models/indb_nutrition_predictor_best.pkl')
print(f"   ✓ models/indb_nutrition_predictor_best.pkl")

results_df.to_csv('models/indb_model_comparison.csv', index=False)
print(f"   ✓ models/indb_model_comparison.csv")

# Visualizations
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

os.makedirs('visualizations', exist_ok=True)

# Plot 1: Model Comparison
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# MAE
axes[0].bar(results_df['Model'], results_df['MAE'], color='coral', edgecolor='black')
axes[0].set_ylabel('MAE (calories)', fontsize=12)
axes[0].set_title('Model Comparison: MAE', fontsize=14, fontweight='bold')
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(axis='y', alpha=0.3)

# RMSE
axes[1].bar(results_df['Model'], results_df['RMSE'], color='steelblue', edgecolor='black')
axes[1].set_ylabel('RMSE (calories)', fontsize=12)
axes[1].set_title('Model Comparison: RMSE', fontsize=14, fontweight='bold')
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(axis='y', alpha=0.3)

# R²
axes[2].bar(results_df['Model'], results_df['R²'], color='green', edgecolor='black')
axes[2].set_ylabel('R² Score', fontsize=12)
axes[2].set_title('Model Comparison: R²', fontsize=14, fontweight='bold')
axes[2].tick_params(axis='x', rotation=45)
axes[2].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/indb_model_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/indb_model_comparison.png")
plt.close()

# Plot 2: Actual vs Predicted (Best Model)
best_predictions = predictions[best_model_name]

plt.figure(figsize=(10, 8))
plt.scatter(y_test, best_predictions, alpha=0.5, edgecolors='k')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Calories', fontsize=12)
plt.ylabel('Predicted Calories', fontsize=12)
plt.title(f'{best_model_name}: Actual vs Predicted', fontsize=14, fontweight='bold')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('visualizations/indb_actual_vs_predicted.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/indb_actual_vs_predicted.png")
plt.close()

# Plot 3: Feature Importance (Random Forest)
if 'Random Forest' in models:
    feature_importance = rf.feature_importances_
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': feature_importance
    }).sort_values('importance', ascending=False).head(15)
    
    plt.figure(figsize=(10, 8))
    plt.barh(importance_df['feature'], importance_df['importance'], color='purple')
    plt.xlabel('Importance', fontsize=12)
    plt.title('Top 15 Most Important Features (Random Forest)', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('visualizations/indb_feature_importance.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: visualizations/indb_feature_importance.png")
    plt.close()

print("\n" + "="*80)
print("✅ TRAINING COMPLETE!")
print("="*80)
print(f"\n🎯 Best Model: {best_model_name}")
print(f"   Accuracy: ±{results_df.iloc[0]['MAE']:.0f} calories")
print(f"   R² Score: {results_df.iloc[0]['R²']:.3f}")
print(f"\n📁 Models saved in: models/")
print(f"📊 Visualizations saved in: visualizations/")
print("="*80)
