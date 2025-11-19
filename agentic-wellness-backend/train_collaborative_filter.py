# File: train_collaborative_filter_simple.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

print("="*80)
print("TIER 3: TRAINING COLLABORATIVE FILTERING (FROM SCRATCH)")
print("="*80)

# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("\n[Step 1] Loading synthetic ratings...")
ratings_df = pd.read_csv('data/synthetic_user_ratings.csv')
print(f"✓ Loaded {len(ratings_df):,} ratings from {ratings_df['user_id'].nunique()} users")

# ============================================================================
# STEP 2: Create User-Item Matrix
# ============================================================================
print("\n[Step 2] Creating user-item rating matrix...")

# Pivot to create matrix: rows=users, columns=recipes, values=ratings
rating_matrix = ratings_df.pivot_table(
    index='user_id',
    columns='recipe_id', 
    values='rating'
).fillna(0)  # Fill missing with 0 (not rated)

print(f"✓ Matrix shape: {rating_matrix.shape} (users × recipes)")
print(f"✓ Sparsity: {(rating_matrix == 0).sum().sum() / rating_matrix.size * 100:.1f}%")

# ============================================================================
# STEP 3: Train-Test Split
# ============================================================================
print("\n[Step 3] Splitting into train/test sets...")

# Convert to long format for splitting
train_df, test_df = train_test_split(ratings_df, test_size=0.2, random_state=42)

print(f"✓ Train: {len(train_df)} ratings")
print(f"✓ Test: {len(test_df)} ratings")

# ============================================================================
# STEP 4: Implement SVD from Scratch using NumPy
# ============================================================================
print("\n" + "="*80)
print("MODEL 1: SVD (Matrix Factorization)")
print("="*80)

print("\n📚 Implementing SVD using NumPy's linear algebra...")

# Create train matrix
train_matrix = train_df.pivot_table(
    index='user_id',
    columns='recipe_id',
    values='rating'
).fillna(0)

# Center the ratings (subtract mean)
user_means = train_matrix.replace(0, np.nan).mean(axis=1)
train_matrix_centered = train_matrix.sub(user_means, axis=0).fillna(0)

# Perform SVD using NumPy
print("  • Computing SVD decomposition...")
U, sigma, Vt = np.linalg.svd(train_matrix_centered, full_matrices=False)

# Keep only top k factors
k = 50
U_k = U[:, :k]
sigma_k = np.diag(sigma[:k])
Vt_k = Vt[:k, :]

print(f"  • Reduced to {k} latent factors")

# Reconstruct matrix
predicted_ratings = np.dot(np.dot(U_k, sigma_k), Vt_k)

# Add back user means
predicted_ratings = predicted_ratings + user_means.values.reshape(-1, 1)

# Clip to valid range [1, 5]
predicted_ratings = np.clip(predicted_ratings, 1, 5)

print("✓ SVD training complete!")

# ============================================================================
# STEP 5: Create Prediction Function
# ============================================================================

class SimpleSVD:
    """Simple SVD-based collaborative filter"""
    
    def __init__(self, U, sigma, Vt, user_means, user_ids, recipe_ids):
        self.U = U
        self.sigma = sigma
        self.Vt = Vt
        self.user_means = user_means
        self.user_ids = user_ids
        self.recipe_ids = recipe_ids
        self.user_id_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
        self.recipe_id_to_idx = {rid: idx for idx, rid in enumerate(recipe_ids)}
    
    def predict(self, user_id, recipe_id):
        """Predict rating for user-recipe pair"""
        try:
            user_idx = self.user_id_to_idx.get(user_id)
            recipe_idx = self.recipe_id_to_idx.get(recipe_id)
            
            if user_idx is None or recipe_idx is None:
                # Unknown user/recipe - return global mean
                return 3.5
            
            # Predict using SVD
            pred = np.dot(np.dot(self.U[user_idx], self.sigma), self.Vt[:, recipe_idx])
            pred += self.user_means.iloc[user_idx]
            
            return np.clip(pred, 1, 5)
        
        except:
            return 3.5  # Default prediction

# Save model
svd_model = SimpleSVD(
    U_k, sigma_k, Vt_k,
    user_means,
    train_matrix.index.tolist(),
    train_matrix.columns.tolist()
)

# ============================================================================
# STEP 6: Evaluate on Test Set
# ============================================================================
print("\n[Step 4] Evaluating SVD model...")

predictions = []
actuals = []

for _, row in test_df.iterrows():
    pred = svd_model.predict(row['user_id'], row['recipe_id'])
    predictions.append(pred)
    actuals.append(row['rating'])

# Calculate metrics
rmse = np.sqrt(mean_squared_error(actuals, predictions))
mae = mean_absolute_error(actuals, predictions)

print(f"\n📊 SVD Performance:")
print(f"  RMSE: {rmse:.4f}")
print(f"  MAE: {mae:.4f}")
print(f"\n💡 On average, predictions are off by {mae:.2f} stars")

# ============================================================================
# STEP 7: Implement Simple User-Based CF
# ============================================================================
print("\n" + "="*80)
print("MODEL 2: User-Based Collaborative Filtering")
print("="*80)

from sklearn.metrics.pairwise import cosine_similarity

print("\n📚 Computing user-user similarities...")

# Compute user similarity matrix
user_similarity = cosine_similarity(train_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=train_matrix.index,
    columns=train_matrix.index
)

print("✓ User similarity matrix computed")

class SimpleUserCF:
    """Simple user-based collaborative filter"""
    
    def __init__(self, rating_matrix, similarity_matrix, k=20):
        self.rating_matrix = rating_matrix
        self.similarity_matrix = similarity_matrix
        self.k = k
        self.global_mean = rating_matrix.replace(0, np.nan).mean().mean()
    
    def predict(self, user_id, recipe_id):
        """Predict rating using k nearest neighbors"""
        try:
            if user_id not in self.similarity_matrix.index:
                return self.global_mean
            
            if recipe_id not in self.rating_matrix.columns:
                return self.global_mean
            
            # Get top k similar users
            similar_users = self.similarity_matrix[user_id].sort_values(ascending=False)[1:self.k+1]
            
            # Get ratings from similar users
            ratings = []
            weights = []
            
            for sim_user, similarity in similar_users.items():
                if similarity > 0:
                    rating = self.rating_matrix.loc[sim_user, recipe_id]
                    if rating > 0:  # User rated this recipe
                        ratings.append(rating)
                        weights.append(similarity)
            
            if len(ratings) == 0:
                return self.global_mean
            
            # Weighted average
            pred = np.average(ratings, weights=weights)
            return np.clip(pred, 1, 5)
        
        except:
            return self.global_mean

user_cf = SimpleUserCF(train_matrix, user_similarity_df, k=20)

# Evaluate
predictions_cf = []
for _, row in test_df.iterrows():
    pred = user_cf.predict(row['user_id'], row['recipe_id'])
    predictions_cf.append(pred)

rmse_cf = np.sqrt(mean_squared_error(actuals, predictions_cf))
mae_cf = mean_absolute_error(actuals, predictions_cf)

print(f"\n📊 User-CF Performance:")
print(f"  RMSE: {rmse_cf:.4f}")
print(f"  MAE: {mae_cf:.4f}")

# ============================================================================
# STEP 8: Compare Models & Save Best
# ============================================================================
print("\n" + "="*80)
print("MODEL COMPARISON")
print("="*80)

results = {
    'Model': ['SVD', 'User-CF'],
    'RMSE': [rmse, rmse_cf],
    'MAE': [mae, mae_cf]
}

comparison_df = pd.DataFrame(results).sort_values('RMSE')
print("\n" + comparison_df.to_string(index=False))

# Save best model
best_model_name = comparison_df.iloc[0]['Model']
best_model = svd_model if best_model_name == 'SVD' else user_cf

print(f"\n🏆 BEST MODEL: {best_model_name}")

os.makedirs('models', exist_ok=True)
joblib.dump(svd_model, 'models/cf_svd.pkl')
joblib.dump(user_cf, 'models/cf_user.pkl')
joblib.dump(best_model, 'models/collaborative_filter_best.pkl')

print("✓ Models saved to 'models/' directory")

# ============================================================================
# STEP 9: Visualizations
# ============================================================================
print("\n[Step 5] Creating visualizations...")
os.makedirs('visualizations', exist_ok=True)

# Plot 1: Model comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.bar(comparison_df['Model'], comparison_df['RMSE'], color='steelblue', edgecolor='black')
ax1.set_ylabel('RMSE (Lower is Better)', fontsize=12)
ax1.set_title('Model Comparison: RMSE', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

ax2.bar(comparison_df['Model'], comparison_df['MAE'], color='coral', edgecolor='black')
ax2.set_ylabel('MAE (Lower is Better)', fontsize=12)
ax2.set_title('Model Comparison: MAE', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/model_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/model_comparison.png")
plt.close()

# Plot 2: Prediction errors
errors = np.array(predictions) - np.array(actuals)
plt.figure(figsize=(10, 6))
plt.hist(errors, bins=30, color='purple', edgecolor='black', alpha=0.7)
plt.xlabel('Prediction Error (Predicted - Actual)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title(f'{best_model_name} Prediction Error Distribution', fontsize=14, fontweight='bold')
plt.axvline(x=0, color='red', linestyle='--', linewidth=2)
plt.grid(axis='y', alpha=0.3)
plt.savefig('visualizations/prediction_errors.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/prediction_errors.png")
plt.close()

print("\n" + "="*80)
print("✅ COLLABORATIVE FILTERING TRAINING COMPLETE!")
print("="*80)
print(f"\nBest Model: {best_model_name}")
print(f"  RMSE: {comparison_df.iloc[0]['RMSE']:.4f}")
print(f"  MAE: {comparison_df.iloc[0]['MAE']:.4f}")
print("\nReady for hybrid integration!")
print("="*80)
