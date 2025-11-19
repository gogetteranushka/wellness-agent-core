# File: prepare_indb_features.py

import pandas as pd
import numpy as np

# Load data
recipes = pd.read_excel('data/recipes.xlsx')
indb = pd.read_excel('data/INDB.xlsx')

print("="*80)
print("FEATURE ENGINEERING FOR INDB")
print("="*80)

# Unit conversion dictionary
UNIT_CONVERSIONS = {
    'tsp': 5,      # 1 tsp = 5g (average)
    'tbsp': 15,    # 1 tbsp = 15g
    'C': 240,      # 1 cup = 240ml/g
    'ml': 1,       # 1ml = 1ml (no conversion)
    'g': 1,        # 1g = 1g (no conversion)
    'kg': 1000,    # 1kg = 1000g
}

def convert_to_grams(amount, unit):
    """Convert various units to grams"""
    if pd.isna(amount) or pd.isna(unit):
        return 0
    
    unit_clean = str(unit).strip().lower()
    
    # Handle common variations
    if 'tsp' in unit_clean or 'teaspoon' in unit_clean:
        return amount * 5
    elif 'tbsp' in unit_clean or 'tablespoon' in unit_clean:
        return amount * 15
    elif 'c' == unit_clean or 'cup' in unit_clean:
        return amount * 240
    elif 'ml' in unit_clean:
        return amount * 1
    elif 'g' == unit_clean or 'gm' in unit_clean or 'gram' in unit_clean:
        return amount * 1
    elif 'kg' in unit_clean:
        return amount * 1000
    else:
        # Default: assume grams
        return amount

def extract_features_for_recipe(recipe_code, recipes_df):
    """
    Extract features for a single recipe
    
    Args:
        recipe_code: Recipe code (e.g., 'ASC001')
        recipes_df: DataFrame with ingredient data
    
    Returns:
        dict: Feature dictionary
    """
    
    # Filter to get all ingredients for this recipe
    recipe_ingredients = recipes_df[recipes_df['recipe_code'] == recipe_code].copy()
    
    if len(recipe_ingredients) == 0:
        return None
    
    features = {}
    
    # 1. Count total ingredients
    features['ingredient_count'] = len(recipe_ingredients)
    
    # 2. Calculate total weight in grams
    recipe_ingredients['amount_grams'] = recipe_ingredients.apply(
        lambda row: convert_to_grams(row['amount'], row['unit']), 
        axis=1
    )
    features['total_weight_grams'] = recipe_ingredients['amount_grams'].sum()
    
    # 3. Check for common ingredients (binary flags)
    all_ingredients = recipe_ingredients['food_name'].str.lower().tolist()
    
    features['has_milk'] = 1 if any('milk' in ing for ing in all_ingredients) else 0
    features['has_sugar'] = 1 if any('sugar' in ing for ing in all_ingredients) else 0
    features['has_rice'] = 1 if any('rice' in ing for ing in all_ingredients) else 0
    features['has_dal'] = 1 if any('dal' in ing or 'lentil' in ing for ing in all_ingredients) else 0
    features['has_paneer'] = 1 if any('paneer' in ing or 'cottage cheese' in ing for ing in all_ingredients) else 0
    features['has_ghee'] = 1 if any('ghee' in ing for ing in all_ingredients) else 0
    features['has_butter'] = 1 if any('butter' in ing for ing in all_ingredients) else 0
    features['has_cream'] = 1 if any('cream' in ing for ing in all_ingredients) else 0
    features['has_oil'] = 1 if any('oil' in ing for ing in all_ingredients) else 0
    features['has_onion'] = 1 if any('onion' in ing for ing in all_ingredients) else 0
    features['has_tomato'] = 1 if any('tomato' in ing for ing in all_ingredients) else 0
    features['has_potato'] = 1 if any('potato' in ing for ing in all_ingredients) else 0
    features['has_chicken'] = 1 if any('chicken' in ing for ing in all_ingredients) else 0
    features['has_vegetables'] = 1 if any('vegetable' in ing or 'carrot' in ing or 'peas' in ing or 'beans' in ing for ing in all_ingredients) else 0
    
    # 4. Calculate category totals
    # Dairy products
    dairy_ingredients = recipe_ingredients[recipe_ingredients['food_name'].str.lower().str.contains('milk|cream|paneer|cheese|butter|ghee|yogurt|curd', na=False)]
    features['dairy_grams'] = dairy_ingredients['amount_grams'].sum()
    
    # Grains
    grain_ingredients = recipe_ingredients[recipe_ingredients['food_name'].str.lower().str.contains('rice|wheat|flour|bread|roti|chapati|naan', na=False)]
    features['grain_grams'] = grain_ingredients['amount_grams'].sum()
    
    # Proteins (dal, lentils, meat)
    protein_ingredients = recipe_ingredients[recipe_ingredients['food_name'].str.lower().str.contains('dal|lentil|chicken|meat|fish|egg|paneer', na=False)]
    features['protein_source_grams'] = protein_ingredients['amount_grams'].sum()
    
    # Fats (oil, ghee, butter)
    fat_ingredients = recipe_ingredients[recipe_ingredients['food_name'].str.lower().str.contains('oil|ghee|butter|fat', na=False)]
    features['fat_source_grams'] = fat_ingredients['amount_grams'].sum()
    
    # Vegetables
    veg_ingredients = recipe_ingredients[recipe_ingredients['food_name'].str.lower().str.contains('vegetable|onion|tomato|potato|carrot|peas|beans|cabbage|spinach|cauliflower', na=False)]
    features['vegetable_grams'] = veg_ingredients['amount_grams'].sum()
    
    # Spices and seasonings
    spice_ingredients = recipe_ingredients[recipe_ingredients['food_name'].str.lower().str.contains('spice|masala|salt|pepper|cumin|turmeric|coriander|chili', na=False)]
    features['spice_grams'] = spice_ingredients['amount_grams'].sum()
    
    # 5. Rich ingredient count (cream, butter, ghee, cheese)
    features['rich_ingredient_count'] = sum([
        features['has_cream'],
        features['has_butter'],
        features['has_ghee'],
        features['has_paneer']
    ])
    
    return features

# Test on first few recipes
print("\n🔍 Testing feature extraction on first 5 recipes:\n")
for recipe_code in recipes['recipe_code'].unique()[:5]:
    features = extract_features_for_recipe(recipe_code, recipes)
    if features:
        recipe_name = recipes[recipes['recipe_code'] == recipe_code]['recipe_name'].iloc[0]
        print(f"\n{'='*60}")
        print(f"Recipe: {recipe_code} - {recipe_name}")
        print(f"{'='*60}")
        for key, value in features.items():
            print(f"  {key:.<35} {value}")

print("\n" + "="*80)
print("✅ Feature extraction working!")
print("="*80)

# Now extract features for ALL recipes
print("\n⏳ Extracting features for all 1,014 recipes...")
all_features = []
all_recipe_codes = []

for recipe_code in recipes['recipe_code'].unique():
    features = extract_features_for_recipe(recipe_code, recipes)
    if features:
        all_features.append(features)
        all_recipe_codes.append(recipe_code)

# Convert to DataFrame
features_df = pd.DataFrame(all_features)
features_df['recipe_code'] = all_recipe_codes

print(f"✅ Extracted features for {len(features_df)} recipes")
print(f"\n📊 Feature DataFrame shape: {features_df.shape}")
print(f"   Rows: {features_df.shape[0]} recipes")
print(f"   Columns: {features_df.shape[1]} features")

# Merge with nutrition targets from INDB
indb_targets = indb[['food_code', 'energy_kcal', 'protein_g', 'carb_g', 'fat_g', 'sodium_mg']].copy()
indb_targets.columns = ['recipe_code', 'calories', 'protein', 'carbs', 'fats', 'sodium']

# Merge
final_df = features_df.merge(indb_targets, on='recipe_code', how='left')

print(f"\n✅ Merged with nutrition targets")
print(f"   Final dataset: {final_df.shape}")

# Save
final_df.to_csv('data/indb_features_with_targets.csv', index=False)
print(f"\n💾 Saved to: data/indb_features_with_targets.csv")

print("\n📊 Preview of final dataset:")
print(final_df.head())

print("\n📊 Feature statistics:")
print(final_df.describe())

print("\n" + "="*80)
print("✅ FEATURE ENGINEERING COMPLETE!")
print("="*80)
print("\nNext step: Train ML models on this feature set!")
