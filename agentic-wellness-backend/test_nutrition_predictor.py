# File: test_nutrition_predictor.py

import requests
import pandas as pd

print("="*80)
print("NUTRITION PREDICTOR - SANITY CHECK")
print("="*80)

API_URL = "http://localhost:5000/api/predict-nutrition"

# Test cases with known values (USDA verified)
test_cases = [
    {
        'name': 'Plain Rice',
        'ingredients': [{'name': 'rice', 'amount': 100, 'unit': 'g'}],
        'expected_calories': (120, 140),  # Range
        'expected_protein': (2, 3.5),
        'should_scale': True
    },
    {
        'name': 'Plain Rice (200g)',
        'ingredients': [{'name': 'rice', 'amount': 200, 'unit': 'g'}],
        'expected_calories': (240, 280),
        'expected_protein': (4, 7),
        'should_scale': True
    },
    {
        'name': 'Tomatoes',
        'ingredients': [{'name': 'tomatoes', 'amount': 100, 'unit': 'g'}],
        'expected_calories': (15, 30),
        'expected_protein': (0.5, 1.5),
        'should_scale': True
    },
    {
        'name': 'Whole Milk',
        'ingredients': [{'name': 'milk', 'amount': 100, 'unit': 'ml'}],
        'expected_calories': (55, 65),
        'expected_protein': (3, 4),
        'should_scale': True
    },
    {
        'name': 'Almonds',
        'ingredients': [{'name': 'almond', 'amount': 100, 'unit': 'g'}],
        'expected_calories': (600, 640),
        'expected_protein': (18, 22),
        'should_scale': True
    },
    {
        'name': 'Chicken Breast',
        'ingredients': [{'name': 'chicken', 'amount': 100, 'unit': 'g'}],
        'expected_calories': (155, 175),
        'expected_protein': (28, 33),
        'should_scale': True
    },
    {
        'name': 'Cooking Oil',
        'ingredients': [{'name': 'oil', 'amount': 10, 'unit': 'ml'}],
        'expected_calories': (85, 92),
        'expected_protein': (0, 0.1),
        'should_scale': True
    },
    {
        'name': 'Egg',
        'ingredients': [{'name': 'egg', 'amount': 50, 'unit': 'g'}],
        'expected_calories': (70, 85),
        'expected_protein': (6, 7),
        'should_scale': True
    },
    {
        'name': 'Simple Dal Rice',
        'ingredients': [
            {'name': 'rice', 'amount': 100, 'unit': 'g'},
            {'name': 'dal', 'amount': 50, 'unit': 'g'},
            {'name': 'oil', 'amount': 5, 'unit': 'ml'}
        ],
        'expected_calories': (230, 280),
        'expected_protein': (7, 11),
        'should_scale': False
    },
    {
        'name': 'Paneer Tikka',
        'ingredients': [
            {'name': 'paneer', 'amount': 100, 'unit': 'g'},
            {'name': 'oil', 'amount': 10, 'unit': 'ml'}
        ],
        'expected_calories': (340, 380),
        'expected_protein': (17, 20),
        'should_scale': False
    },
]

results = []
passed = 0
failed = 0

print("\n🧪 Running tests...\n")

for i, test in enumerate(test_cases, 1):
    try:
        # Make API request
        response = requests.post(API_URL, json={'ingredients': test['ingredients']})
        
        if response.status_code != 200:
            print(f"❌ Test {i}: {test['name']} - API Error {response.status_code}")
            failed += 1
            continue
        
        data = response.json()
        predicted = data['predicted_nutrition']
        
        # Extract values
        cal = predicted['calories']
        protein = predicted['protein_g']
        carbs = predicted['carbs_g']
        fat = predicted['fat_g']
        
        # Check if in expected range
        cal_ok = test['expected_calories'][0] <= cal <= test['expected_calories'][1]
        protein_ok = test['expected_protein'][0] <= protein <= test['expected_protein'][1]
        
        # Check macro math: (protein*4) + (carbs*4) + (fat*9) ≈ calories (±10%)
        computed_cal = (protein * 4) + (carbs * 4) + (fat * 9)
        macro_math_ok = abs(computed_cal - cal) / cal < 0.15  # 15% tolerance
        
        # Overall pass/fail
        test_passed = cal_ok and protein_ok and macro_math_ok
        
        if test_passed:
            print(f"✅ Test {i}: {test['name']}")
            passed += 1
        else:
            print(f"❌ Test {i}: {test['name']}")
            if not cal_ok:
                print(f"   Calories: {cal} kcal (expected {test['expected_calories'][0]}-{test['expected_calories'][1]})")
            if not protein_ok:
                print(f"   Protein: {protein}g (expected {test['expected_protein'][0]}-{test['expected_protein'][1]})")
            if not macro_math_ok:
                print(f"   Macro math: {computed_cal:.1f} computed vs {cal} reported (off by {abs(computed_cal-cal):.1f})")
            failed += 1
        
        # Store results
        results.append({
            'test_name': test['name'],
            'ingredients': ', '.join([f"{ing['amount']}{ing['unit']} {ing['name']}" for ing in test['ingredients']]),
            'predicted_cal': cal,
            'expected_cal_min': test['expected_calories'][0],
            'expected_cal_max': test['expected_calories'][1],
            'predicted_protein': protein,
            'predicted_carbs': carbs,
            'predicted_fat': fat,
            'macro_math_check': f"{computed_cal:.1f}",
            'status': 'PASS' if test_passed else 'FAIL'
        })
        
        print(f"   {cal} kcal | P:{protein}g C:{carbs}g F:{fat}g")
        print()
        
    except Exception as e:
        print(f"❌ Test {i}: {test['name']} - Error: {e}")
        failed += 1
        print()

# Summary
print("="*80)
print("TEST SUMMARY")
print("="*80)
print(f"✅ Passed: {passed}/{len(test_cases)}")
print(f"❌ Failed: {failed}/{len(test_cases)}")
print(f"Success Rate: {passed/len(test_cases)*100:.1f}%")

# Save detailed results
df = pd.DataFrame(results)
df.to_csv('nutrition_predictor_test_results.csv', index=False)
print(f"\n📄 Detailed results saved: nutrition_predictor_test_results.csv")

print("\n" + "="*80)
if passed == len(test_cases):
    print("🎉 ALL TESTS PASSED - Model is production ready!")
elif passed >= len(test_cases) * 0.8:
    print("⚠️  MOSTLY PASSING - Good enough for demo")
else:
    print("❌ MULTIPLE FAILURES - Needs debugging")
print("="*80)
