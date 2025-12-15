import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 80)
print("Testing Complete Meal Plan API")
print("=" * 80)

user_data = {
    "age": 55,
    "gender": "M",
    "weight_kg": 90,
    "height_cm": 175,
    "activity_level": "sedentary",
    "goal": "weight_loss",
    "medical_conditions": ["diabetes", "hypertension"],
    "diet_type": "Vegetarian",
    
}

try:
    response = requests.post(f"{BASE_URL}/diet/complete-meal-plan", json=user_data)
    
    # Print raw response for debugging
    print(f"\nHTTP Status Code: {response.status_code}")
    print(f"\nRaw Response:")
    print(response.text)
    print()
    
    # Try to parse JSON
    try:
        result = response.json()
    except:
        print("❌ Error: Response is not valid JSON")
        exit(1)
    
    # Check response structure
    if 'status' in result and result['status'] == 'success':
        data = result['data']
        
        print("✅ SUCCESS - NUTRITION TARGETS:")
        print(f"  Daily Calories: {data['nutrition_targets']['target_calories']}")
        print(f"  Protein: {data['nutrition_targets']['daily_macros']['protein_g']}g")
        print(f"  Carbs: {data['nutrition_targets']['daily_macros']['carbs_g']}g")
        print(f"  Fat: {data['nutrition_targets']['daily_macros']['fat_g']}g")
        
        print("\n✅ MEAL PLANS:")
        for meal, recipes in data['meal_plans'].items():
            print(f"\n{meal.upper()}:")
            for i, recipe in enumerate(recipes, 1):
                print(f"  {i}. {recipe['recipe_name']} ({recipe['nutrition']['calories']:.0f} cal)")
                print(f"     Match Score: {recipe['match_score']:.1f}/100")
                if recipe.get('protein_suggestion'):
                    print(f"     💡 {recipe['protein_suggestion']}")
    
    elif 'error' in result:
        print(f"❌ API Error: {result['error']}")
        if 'message' in result:
            print(f"   Details: {result['message']}")
    
    else:
        print("❌ Unexpected response format:")
        print(json.dumps(result, indent=2))

except requests.exceptions.ConnectionError:
    print("❌ Error: Cannot connect to Flask server")
    print("   Make sure Flask is running: python app.py")

except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    import traceback
    traceback.print_exc()
