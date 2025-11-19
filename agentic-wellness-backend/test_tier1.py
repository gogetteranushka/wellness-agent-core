# Test script
from diet_engine import DietEngine

engine = DietEngine()

# Test case 1: Vegetarian with diabetes
user1 = {
    'age': 55,
    'gender': 'M',
    'weight_kg': 90,
    'height_cm': 175,
    'activity_level': 'sedentary',
    'goal': 'weight_loss',
    'medical_conditions': ['diabetes', 'hypertension'],
    'diet_type': 'Vegetarian'
}

plan1 = engine.generate_personalized_plan(user1)
print("Test 1 - Vegetarian with Diabetes:")
print(f"  Calories: {plan1['target_calories']}")
print(f"  Macros: {plan1['daily_macros']}")
print(f"  Breakfast: {plan1['meal_breakdown']['breakfast']}")

# Test case 2: Non-veg muscle gain
user2 = {
    'age': 25,
    'gender': 'M',
    'weight_kg': 70,
    'height_cm': 175,
    'activity_level': 'very_active',
    'goal': 'muscle_gain',
    'medical_conditions': [],
    'diet_type': 'Non Vegeterian'
}

plan2 = engine.generate_personalized_plan(user2)
print("\nTest 2 - Non-veg Muscle Gain:")
print(f"  Calories: {plan2['target_calories']}")
print(f"  Macros: {plan2['daily_macros']}")

# Test case 3: Missing diet_type (should default to Vegetarian)
user3 = {
    'age': 30,
    'gender': 'F',
    'weight_kg': 60,
    'height_cm': 165,
    'activity_level': 'moderately_active',
    'goal': 'maintenance',
    'medical_conditions': []
    # diet_type not specified - should default
}

plan3 = engine.generate_personalized_plan(user3)
print("\nTest 3 - Default Diet Type:")
print(f"  Calories: {plan3['target_calories']}")
print(f"  Macros: {plan3['daily_macros']}")
