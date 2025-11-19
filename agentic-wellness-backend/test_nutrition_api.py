# File: test_nutrition_api.py

import requests
import json

BASE_URL = 'http://localhost:5000'

print("="*80)
print("NUTRITION PREDICTION API - TEST SCRIPT")
print("="*80)

# Test Case 1: Dal Makhani
print("\n[Test 1] Dal Makhani")
print("-" * 40)

dal_makhani = {
    "ingredients": [
        {"name": "urad dal", "amount": 200, "unit": "g"},
        {"name": "butter", "amount": 30, "unit": "g"},
        {"name": "cream", "amount": 50, "unit": "ml"},
        {"name": "tomato", "amount": 100, "unit": "g"},
        {"name": "onion", "amount": 50, "unit": "g"},
        {"name": "ginger-garlic paste", "amount": 10, "unit": "g"},
        {"name": "spices", "amount": 5, "unit": "g"}
    ]
}

response = requests.post(f'{BASE_URL}/api/predict-nutrition', json=dal_makhani)
result = response.json()

print(f"Predicted Calories: {result['predicted_nutrition']['calories']} kcal")
print(f"Confidence Range: {result['predicted_nutrition']['confidence_range']['min']}-{result['predicted_nutrition']['confidence_range']['max']} kcal")
print(f"Model: {result['model_info']['algorithm']}")
print(f"Accuracy: {result['model_info']['accuracy']}")

# Test Case 2: Simple Rice Bowl
print("\n[Test 2] Simple Rice Bowl")
print("-" * 40)

rice_bowl = {
    "ingredients": [
        {"name": "rice", "amount": 150, "unit": "g"},
        {"name": "dal", "amount": 50, "unit": "g"},
        {"name": "ghee", "amount": 10, "unit": "g"}
    ]
}

response = requests.post(f'{BASE_URL}/api/predict-nutrition', json=rice_bowl)
result = response.json()

print(f"Predicted Calories: {result['predicted_nutrition']['calories']} kcal")
print(f"Confidence Range: {result['predicted_nutrition']['confidence_range']['min']}-{result['predicted_nutrition']['confidence_range']['max']} kcal")

# Test Case 3: Using Pre-calculated Features
print("\n[Test 3] Paneer Tikka (Pre-calculated Features)")
print("-" * 40)

paneer_tikka_features = {
    "features": {
        "ingredient_count": 8,
        "total_weight_grams": 350,
        "has_milk": 0,
        "has_sugar": 0,
        "has_rice": 0,
        "has_dal": 0,
        "has_paneer": 1,
        "has_ghee": 0,
        "has_butter": 0,
        "has_cream": 0,
        "has_oil": 1,
        "has_onion": 1,
        "has_tomato": 0,
        "has_potato": 0,
        "has_chicken": 0,
        "has_vegetables": 1,
        "dairy_grams": 200,
        "grain_grams": 0,
        "protein_source_grams": 200,
        "fat_source_grams": 20,
        "vegetable_grams": 50,
        "spice_grams": 10,
        "rich_ingredient_count": 1
    }
}

response = requests.post(f'{BASE_URL}/api/predict-nutrition', json=paneer_tikka_features)
result = response.json()

print(f"Predicted Calories: {result['predicted_nutrition']['calories']} kcal")
print(f"Confidence Range: {result['predicted_nutrition']['confidence_range']['min']}-{result['predicted_nutrition']['confidence_range']['max']} kcal")

print("\n" + "="*80)
print("✅ ALL TESTS COMPLETE!")
print("="*80)
