# File: test_complete_system.py

import pandas as pd
from diet_engine import DietEngine
from recipe_recommender import MedicalAwareRecipeRecommender

# Load recipes
recipes = pd.read_csv('data/recipe_nutrients_cleaned.csv')

# Initialize systems
diet_engine = DietEngine()
recommender = MedicalAwareRecipeRecommender(recipes)

# Test user: 55yo with diabetes + hypertension
user_profile = {
    'age': 55,
    'gender': 'M',
    'weight_kg': 90,
    'height_cm': 175,
    'activity_level': 'sedentary',
    'goal': 'weight_loss',
    'medical_conditions': ['diabetes', 'hypertension'],
    'diet_type': 'Vegetarian'
}

# TIER 1: Generate targets
plan = diet_engine.generate_personalized_plan(user_profile)

print("=" * 80)
print("FITMINAI - MEDICAL-AWARE DIET PLAN")
print("=" * 80)
print(f"\nUser: {user_profile['age']}yo, {user_profile['weight_kg']}kg")
print(f"Medical Conditions: {', '.join(user_profile['medical_conditions'])}")
print(f"\nTIER 1 Targets:")
print(f"  Daily Calories: {plan['target_calories']}")
print(f"  Protein: {plan['daily_macros']['protein_g']}g ({plan['daily_macros']['protein_percent']}%)")
print(f"  Carbs: {plan['daily_macros']['carbs_g']}g ({plan['daily_macros']['carbs_percent']}%)")
print(f"  Fat: {plan['daily_macros']['fat_g']}g ({plan['daily_macros']['fat_percent']}%)")

# TIER 2: Get breakfast recommendations
breakfast_targets = {
    'course': 'Breakfast',
    'calories': plan['meal_breakdown']['breakfast']['calories'],
    'protein_g': plan['meal_breakdown']['breakfast']['protein_g'],
    'carbs_g': plan['meal_breakdown']['breakfast']['carbs_g'],
    'fat_g': plan['meal_breakdown']['breakfast']['fat_g'],
    'diet': user_profile['diet_type'],
    'max_time_mins': 45
}

recommendations, display = recommender.recommend_with_display(
    breakfast_targets,
    medical_conditions=user_profile['medical_conditions'],
    top_n=5
)

print(display)
