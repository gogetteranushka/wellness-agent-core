import pandas as pd
import os

print("="*80)
print("PROCESSING USDA FOUNDATION FOODS DATA")
print("="*80)

# Path to extracted CSV files
data_dir = 'FoodData_Central_foundation_food_csv_2025-04'

# Load tables
print("\n📂 Loading USDA tables...")
food = pd.read_csv('data/food.csv')
food_nutrient = pd.read_csv('data/food_nutrient.csv')
nutrient = pd.read_csv('data/nutrient.csv')

print(f"✓ {len(food)} foods")
print(f"✓ {len(food_nutrient)} nutrient records")
print(f"✓ {len(nutrient)} nutrient types")

# Key nutrient IDs (USDA standard)
NUTRIENT_MAP = {
    1008: 'calories',      # Energy (kcal)
    1003: 'protein',       # Protein (g)
    1005: 'carbs',         # Carbohydrate (g)
    1004: 'fat',           # Total lipid (fat) (g)
    1093: 'sodium',        # Sodium (mg)
}

# Pivot nutrients to columns
print("\n🔧 Pivoting nutrient data...")
food_nutrient_filtered = food_nutrient[food_nutrient['nutrient_id'].isin(NUTRIENT_MAP.keys())]
food_nutrient_filtered['nutrient_name'] = food_nutrient_filtered['nutrient_id'].map(NUTRIENT_MAP)

pivoted = food_nutrient_filtered.pivot_table(
    index='fdc_id',
    columns='nutrient_name',
    values='amount',
    aggfunc='first'
).reset_index()

# Merge with food names
result = food[['fdc_id', 'description']].merge(pivoted, on='fdc_id', how='inner')

# Clean up
result = result.rename(columns={'description': 'ingredient_name'})
result['ingredient_name'] = result['ingredient_name'].str.lower().str.strip()

# Filter out missing data
result = result.dropna(subset=['calories', 'protein', 'carbs', 'fat'])

# All USDA values are per 100g, so rename columns
result = result.rename(columns={
    'calories': 'calories_per_100g',
    'protein': 'protein_per_100g',
    'carbs': 'carbs_per_100g',
    'fat': 'fat_per_100g',
    'sodium': 'sodium_per_100mg'
})

# Fill missing sodium with 0
result['sodium_per_100mg'] = result['sodium_per_100mg'].fillna(0)

# Save
os.makedirs('data', exist_ok=True)
output_path = 'data/usda_ingredients.csv'
result[['ingredient_name', 'calories_per_100g', 'protein_per_100g', 
        'carbs_per_100g', 'fat_per_100g', 'sodium_per_100mg']].to_csv(output_path, index=False)

print(f"\n✅ Saved: {output_path}")
print(f"📊 Total ingredients: {len(result)}")
print("\n📋 Sample:")
print(result.head(10)[['ingredient_name', 'calories_per_100g', 'protein_per_100g']].to_string(index=False))

print("\n" + "="*80)
print("✅ USDA DATA PROCESSED SUCCESSFULLY")
print("="*80)
