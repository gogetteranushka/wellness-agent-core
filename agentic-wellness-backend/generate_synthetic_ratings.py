# File: generate_synthetic_ratings.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("TIER 3: GENERATING SYNTHETIC USER RATINGS")
print("="*80)

# ============================================================================
# STEP 1: Load Recipe Data
# ============================================================================
print("\n[Step 1] Loading recipe dataset...")
recipes_df = pd.read_csv('data/recipe_nutrients_cleaned.csv')
print(f"✓ Loaded {len(recipes_df)} recipes")

# ============================================================================
# STEP 2: Define User Personas
# ============================================================================
print("\n[Step 2] Defining user personas...")

# Configuration
NUM_USERS = 100
MIN_RATINGS_PER_USER = 15
MAX_RATINGS_PER_USER = 25
np.random.seed(42)  # For reproducibility in academic context

# User persona weights (must sum to 1.0)
personas = [
    {'type': 'health_conscious', 'weight': 0.25, 'base_rating': 3.2, 'rating_std': 0.7},
    {'type': 'foodie', 'weight': 0.20, 'base_rating': 3.5, 'rating_std': 0.6},
    {'type': 'traditional', 'weight': 0.20, 'base_rating': 3.8, 'rating_std': 0.5},
    {'type': 'time_constrained', 'weight': 0.20, 'base_rating': 3.4, 'rating_std': 0.6},
    {'type': 'diet_restricted', 'weight': 0.15, 'base_rating': 3.3, 'rating_std': 0.7}
]

print(f"✓ Created {len(personas)} persona types")
for p in personas:
    print(f"   - {p['type']}: {int(p['weight']*100)}% of users")

# ============================================================================
# STEP 3: Rating Generation Logic
# ============================================================================

def assign_persona():
    """
    Randomly assign a persona to a user based on weights
    
    Returns: persona_type (string)
    """
    persona_types = [p['type'] for p in personas]
    weights = [p['weight'] for p in personas]
    return np.random.choice(persona_types, p=weights)


def get_persona_params(persona_type):
    """Get base rating and std dev for a persona"""
    for p in personas:
        if p['type'] == persona_type:
            return p['base_rating'], p['rating_std']
    return 3.5, 0.6  # Default


def calculate_rating(persona_type, recipe):
    """
    Calculate realistic rating based on persona preferences and recipe attributes
    
    This is where the MAGIC happens - we simulate realistic user behavior!
    
    Args:
        persona_type (str): User's persona
        recipe (pd.Series): Recipe data with all attributes
    
    Returns:
        int: Rating from 1 to 5
    
    Algorithm:
        1. Start with persona's base rating tendency
        2. Apply preference boosts/penalties based on recipe attributes
        3. Add realistic noise (users are inconsistent!)
        4. Add individual user bias (some always rate high/low)
        5. Clip to valid range [1, 5]
        6. Round to integer (real ratings are discrete)
    """
    
    # Get persona's base rating tendency
    base_rating, rating_std = get_persona_params(persona_type)
    
    # Start with base
    rating = base_rating
    
    # ========================================================================
    # PERSONA-SPECIFIC PREFERENCES
    # ========================================================================
    
    if persona_type == 'health_conscious':
        # Boost for low-calorie recipes
        if recipe['energy_per_serving'] < 300:
            rating += 1.5
        elif recipe['energy_per_serving'] < 400:
            rating += 0.8
        elif recipe['energy_per_serving'] > 600:
            rating -= 1.0  # Penalty for high-calorie
        
        # Boost for high-protein recipes
        if recipe['protein_per_serving'] > 20:
            rating += 1.2
        elif recipe['protein_per_serving'] > 15:
            rating += 0.7
        elif recipe['protein_per_serving'] < 5:
            rating -= 0.8  # Penalty for low-protein
        
        # Penalty for high-fat recipes
        if recipe['fat_per_serving'] > 20:
            rating -= 1.0
        elif recipe['fat_per_serving'] < 5:
            rating += 0.5
    
    elif persona_type == 'foodie':
        # Boost for exotic/international cuisines
        exotic_cuisines = ['Continental', 'Mexican', 'Italian', 'Asian', 'French']
        if recipe['Cuisine'] in exotic_cuisines:
            rating += 1.3
        
        # Boost for complex recipes (longer cooking time = more interesting)
        if recipe['TotalTimeInMins'] > 60:
            rating += 0.9
        elif recipe['TotalTimeInMins'] > 45:
            rating += 0.5
        elif recipe['TotalTimeInMins'] < 15:
            rating -= 0.7  # Too simple for foodies
    
    elif persona_type == 'traditional':
        # Strong boost for Indian cuisines
        indian_cuisines = ['Indian', 'North Indian', 'South Indian', 'Bengali', 
                          'Punjabi', 'Gujarati', 'Maharashtrian']
        if any(cuisine in recipe['Cuisine'] for cuisine in indian_cuisines):
            rating += 1.6
        else:
            rating -= 1.2  # Don't like foreign food
        
        # Preference for familiar ingredients
        traditional_ingredients = ['paneer', 'dal', 'rice', 'roti', 'curry']
        if any(ing in str(recipe['Ingredients']).lower() for ing in traditional_ingredients):
            rating += 0.6
    
    elif persona_type == 'time_constrained':
        # Strong boost for quick recipes
        if recipe['TotalTimeInMins'] <= 20:
            rating += 1.5
        elif recipe['TotalTimeInMins'] <= 30:
            rating += 1.0
        elif recipe['TotalTimeInMins'] > 45:
            rating -= 1.3  # Major penalty for slow recipes
        
        # Boost for simple recipes (fewer ingredients = easier)
        # Note: This is a simplification since we don't have ingredient count
        if recipe['TotalTimeInMins'] <= 30:
            rating += 0.4
    
    elif persona_type == 'diet_restricted':
        # Boost for diabetic-friendly recipes
        if 'Diabetic' in recipe['Diet'] or 'Sugar Free' in recipe['Diet']:
            rating += 1.7
        
        # Boost for low-sodium (hypertension-friendly)
        if recipe['sodium_per_serving'] < 200:
            rating += 1.3
        elif recipe['sodium_per_serving'] < 400:
            rating += 0.7
        elif recipe['sodium_per_serving'] > 800:
            rating -= 1.5  # Unsafe for hypertension
        
        # Boost for low-carb (diabetes-friendly)
        if recipe['carbohydrate_per_serving'] < 20:
            rating += 1.0
        elif recipe['carbohydrate_per_serving'] > 50:
            rating -= 1.0
    
    # ========================================================================
    # ADD REALISTIC NOISE
    # ========================================================================
    
    # Random noise based on persona's standard deviation
    # This makes ratings realistic - people are inconsistent!
    noise = np.random.normal(0, rating_std)
    
    # Individual user bias (some users always rate high/low)
    # This is CRITICAL for collaborative filtering to work!
    user_bias = np.random.normal(0, 0.4)
    
    # Combine everything
    final_rating = rating + noise + user_bias
    
    # ========================================================================
    # CLIP AND ROUND
    # ========================================================================
    
    # Clip to valid range
    final_rating = np.clip(final_rating, 1.0, 5.0)
    
    # Round to nearest integer (real ratings are 1, 2, 3, 4, 5)
    return int(round(final_rating))


# ============================================================================
# STEP 4: Generate Ratings
# ============================================================================
print("\n[Step 3] Generating user ratings...")

ratings_list = []
user_personas = {}  # Track each user's persona for analysis

for user_id in range(1, NUM_USERS + 1):
    # Assign persona to this user
    persona = assign_persona()
    user_personas[user_id] = persona
    
    # Each user rates between 15-25 recipes
    num_ratings = np.random.randint(MIN_RATINGS_PER_USER, MAX_RATINGS_PER_USER + 1)
    
    # Sample random recipes (without replacement)
    sampled_recipes = recipes_df.sample(num_ratings)
    
    for _, recipe in sampled_recipes.iterrows():
        # Calculate rating
        rating = calculate_rating(persona, recipe)
        
        # Generate realistic timestamp (last 90 days)
        days_ago = np.random.randint(0, 90)
        timestamp = datetime.now() - timedelta(days=days_ago)
        
        # Store rating
        ratings_list.append({
            'user_id': user_id,
            'recipe_id': int(recipe['Srno']),
            'recipe_name': recipe['RecipeName'],
            'rating': rating,
            'timestamp': timestamp,
            'user_persona': persona
        })

# Create DataFrame
ratings_df = pd.DataFrame(ratings_list)

# ============================================================================
# STEP 5: Save and Analyze
# ============================================================================
print("\n[Step 4] Saving results...")

# Save to CSV
output_file = 'synthetic_user_ratings.csv'
ratings_df.to_csv(output_file, index=False)

# Save user personas for later analysis
personas_df = pd.DataFrame([
    {'user_id': uid, 'persona': persona} 
    for uid, persona in user_personas.items()
])
personas_df.to_csv('user_personas.csv', index=False)

print(f"✓ Saved ratings to: {output_file}")
print(f"✓ Saved user personas to: user_personas.csv")

# ============================================================================
# STEP 6: Statistics & Validation
# ============================================================================
print("\n" + "="*80)
print("STATISTICS & VALIDATION")
print("="*80)

print(f"\n📊 Dataset Size:")
print(f"   Total ratings: {len(ratings_df):,}")
print(f"   Unique users: {ratings_df['user_id'].nunique()}")
print(f"   Unique recipes: {ratings_df['recipe_id'].nunique()}")
print(f"   Avg ratings per user: {len(ratings_df) / NUM_USERS:.1f}")
print(f"   Coverage: {ratings_df['recipe_id'].nunique() / len(recipes_df) * 100:.1f}% of recipes")

print(f"\n📊 Rating Distribution:")
rating_counts = ratings_df['rating'].value_counts().sort_index()
for rating, count in rating_counts.items():
    pct = count / len(ratings_df) * 100
    bar = '█' * int(pct / 2)
    print(f"   {rating} stars: {count:4d} ({pct:5.1f}%) {bar}")

print(f"\n📊 Statistical Summary:")
print(f"   Mean rating: {ratings_df['rating'].mean():.2f}")
print(f"   Median rating: {ratings_df['rating'].median():.0f}")
print(f"   Std deviation: {ratings_df['rating'].std():.2f}")
print(f"   Min rating: {ratings_df['rating'].min()}")
print(f"   Max rating: {ratings_df['rating'].max()}")

print(f"\n📊 Persona Distribution:")
persona_counts = ratings_df['user_persona'].value_counts()
for persona, count in persona_counts.items():
    pct = count / len(ratings_df) * 100
    print(f"   {persona}: {count} ratings ({pct:.1f}%)")

# ============================================================================
# STEP 7: Visualizations
# ============================================================================
print("\n[Step 5] Creating visualizations...")

# Create visualizations directory
import os
os.makedirs('visualizations', exist_ok=True)

# Plot 1: Rating Distribution
plt.figure(figsize=(10, 6))
sns.histplot(data=ratings_df, x='rating', bins=5, kde=True, color='steelblue')
plt.xlabel('Rating (1-5 stars)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Distribution of User Ratings (Synthetic Data)', fontsize=14, fontweight='bold')
plt.xticks([1, 2, 3, 4, 5])
plt.grid(axis='y', alpha=0.3)
plt.savefig('visualizations/rating_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/rating_distribution.png")
plt.close()

# Plot 2: Ratings by Persona
plt.figure(figsize=(12, 6))
sns.boxplot(data=ratings_df, x='user_persona', y='rating', palette='Set2')
plt.xlabel('User Persona', fontsize=12)
plt.ylabel('Rating', fontsize=12)
plt.title('Rating Distribution by User Persona', fontsize=14, fontweight='bold')
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.savefig('visualizations/ratings_by_persona.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/ratings_by_persona.png")
plt.close()

# Plot 3: Ratings per User
ratings_per_user = ratings_df.groupby('user_id').size()
plt.figure(figsize=(10, 6))
plt.hist(ratings_per_user, bins=20, color='coral', edgecolor='black')
plt.xlabel('Number of Ratings per User', fontsize=12)
plt.ylabel('Number of Users', fontsize=12)
plt.title('User Engagement Distribution', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
plt.savefig('visualizations/user_engagement.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/user_engagement.png")
plt.close()

print("\n" + "="*80)
print("✅ SYNTHETIC DATA GENERATION COMPLETE!")
print("="*80)
print("\nNext steps:")
print("1. Review the visualizations in the 'visualizations' folder")
print("2. Check if rating distribution looks realistic (should be slightly positive-skewed)")
print("3. Ready to proceed to STEP 2: Training Collaborative Filtering Models")
print("="*80)
