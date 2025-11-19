import requests
import json

BASE_URL = "http://localhost:5000/api"

print("="*80)
print("Testing Hybrid API (TIER 2 + TIER 3)")
print("="*80)

# Test data
test_user = {
    "user_id": 1,
    "meal": "breakfast",
    "calories": 400,
    "protein_g": 20,
    "carbs_g": 40,
    "fat_g": 15,
    "diet": "Vegetarian",
    "medical_conditions": ["diabetes", "hypertension"],
    "max_time_mins": 45,
    "top_n": 3
}

print(f"\n🔍 Requesting recommendations for User {test_user['user_id']}...")
print(f"   Meal: {test_user['meal']}")
print(f"   Medical: {', '.join(test_user['medical_conditions'])}")

response = requests.post(f"{BASE_URL}/diet/recommend-hybrid", json=test_user)
result = response.json()

if result['status'] == 'success':
    data = result['data']
    
    print(f"\n✅ Success! Got {data['count']} hybrid recommendations")
    print(f"\n📊 Model Info:")
    print(f"   • {data['model_info']['tier2']}")
    print(f"   • {data['model_info']['tier3']}")
    print(f"   • {data['model_info']['combination']}")
    
    print(f"\n🍽️  RECOMMENDATIONS:\n")
    
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"{i}. {rec['recipe_name']}")
        print(f"   Hybrid Score: {rec['scores']['hybrid_overall']:.1f}/100")
        print(f"     └─ Nutrition: {rec['scores']['tier2_nutrition']:.1f}/100")
        print(f"     └─ Preference: {rec['scores']['tier3_preference']:.1f}/100")
        print(f"   Nutrition: {rec['nutrition']['calories']:.0f} cal | "
              f"{rec['nutrition']['protein_g']:.1f}g P | "
              f"{rec['nutrition']['carbs_g']:.1f}g C")
        print(f"   Time: {rec['time_mins']} minutes")
        if rec['protein_suggestion']:
            print(f"   💡 {rec['protein_suggestion']}")
        print()
    
    print("="*80)
    print("✅ API TEST SUCCESSFUL!")
    print("="*80)
    
else:
    print(f"\n❌ Error: {result}")
