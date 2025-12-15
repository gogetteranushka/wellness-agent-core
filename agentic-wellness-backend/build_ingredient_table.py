# File: build_ingredient_table.py

import pandas as pd
import json
import numpy as np
from collections import defaultdict

print("="*80)
print("BUILDING INGREDIENT NUTRITION TABLE FROM RECIPES")
print("="*80)

# Load the full recipe dataset
print("\n📂 Loading recipe_nutrients_cleaned.csv...")
df = pd.read_csv('data/recipe_nutrients_cleaned.csv')
print(f"✓ Loaded {len(df)} recipes")

# Dictionary to collect all instances of each ingredient
ingredient_data = defaultdict(lambda: {
    'calories': [],
    'protein': [],
    'carbs': [],
    'fat': [],
    'sodium': [],
    'quantities_g': []
})

# Parse each recipe
# Parse each recipe
print("\n🔍 Parsing ingredient nutrients from recipes...")
parsed_count = 0
failed_count = 0

for idx, row in df.iterrows():
    if idx % 100 == 0:
        print(f"  Processing recipe {idx}/{len(df)}...")
    
    try:
        # Get the columns directly (they're already parsed)
        nutrients = row.get('ingredient_nutrients')
        ing_list = row.get('ingredient_list')
        quantities = row.get('ingredient_quantities_g')
        
        # Skip if missing or empty
        if pd.isna(nutrients) or not nutrients or nutrients == '[]':
            failed_count += 1
            continue
        
        # If they're strings, parse them
        if isinstance(nutrients, str):
            nutrients = eval(nutrients)
        if isinstance(ing_list, str):
            ing_list = eval(ing_list)
        if isinstance(quantities, str):
            quantities = eval(quantities)
        
        # Process each ingredient in this recipe
        if isinstance(nutrients, list) and len(nutrients) > 0:
            for i, nut in enumerate(nutrients):
                if not isinstance(nut, dict):
                    continue
                
                ing_name = ing_list[i] if i < len(ing_list) else f"unknown_{i}"
                ing_name = str(ing_name).lower().strip()
                
                quantity_g = float(quantities[i]) if i < len(quantities) else 100.0
                
                # Extract nutrients
                cal = float(nut.get('energy', 0) or 0)
                prot = float(nut.get('protein', 0) or 0)
                carb = float(nut.get('carbohydrate', 0) or 0)
                fat = float(nut.get('fat', 0) or 0)
                sod = float(nut.get('sodium', 0) or 0)
                
                # Only store if values are non-zero
                if cal > 0 or prot > 0 or carb > 0:
                    ingredient_data[ing_name]['calories'].append(cal)
                    ingredient_data[ing_name]['protein'].append(prot)
                    ingredient_data[ing_name]['carbs'].append(carb)
                    ingredient_data[ing_name]['fat'].append(fat)
                    ingredient_data[ing_name]['sodium'].append(sod)
                    ingredient_data[ing_name]['quantities_g'].append(quantity_g)
        
        parsed_count += 1
        
    except Exception as e:
        failed_count += 1
        if failed_count < 5:  # Print first few errors for debugging
            print(f"  Error on recipe {idx}: {e}")
        continue


print(f"\n✓ Successfully parsed {parsed_count} recipes")
print(f"✗ Failed to parse {failed_count} recipes")
print(f"✓ Extracted data for {len(ingredient_data)} unique ingredients")

# Compute averages per 100g
print("\n📊 Computing per-100g averages...")
ingredient_table = []

for ing_name, data in ingredient_data.items():
    if len(data['calories']) == 0:
        continue
    
    total_instances = len(data['calories'])
    
    # Convert each instance to per-100g, then average
    cal_per_100g_list = []
    prot_per_100g_list = []
    carb_per_100g_list = []
    fat_per_100g_list = []
    sod_per_100g_list = []
    
    for i in range(total_instances):
        qty = data['quantities_g'][i]
        if qty > 0:
            cal_per_100g_list.append(data['calories'][i] / qty * 100)
            prot_per_100g_list.append(data['protein'][i] / qty * 100)
            carb_per_100g_list.append(data['carbs'][i] / qty * 100)
            fat_per_100g_list.append(data['fat'][i] / qty * 100)
            sod_per_100g_list.append(data['sodium'][i] / qty * 100)
    
    if len(cal_per_100g_list) == 0:
        continue
    
    # Take median to avoid outliers
    avg_cal_per_100g = np.median(cal_per_100g_list)
    avg_prot_per_100g = np.median(prot_per_100g_list)
    avg_carb_per_100g = np.median(carb_per_100g_list)
    avg_fat_per_100g = np.median(fat_per_100g_list)
    avg_sod_per_100g = np.median(sod_per_100g_list)
    
    ingredient_table.append({
        'ingredient_name': ing_name,
        'calories_per_100g': round(avg_cal_per_100g, 1),
        'protein_per_100g': round(avg_prot_per_100g, 1),
        'carbs_per_100g': round(avg_carb_per_100g, 1),
        'fat_per_100g': round(avg_fat_per_100g, 1),
        'sodium_per_100g': round(avg_sod_per_100g, 1),
        'sample_count': total_instances
    })

# Convert to DataFrame
ingredient_df = pd.DataFrame(ingredient_table)

# Check if empty
if len(ingredient_df) == 0:
    print("\n❌ ERROR: No ingredients were extracted!")
    print("This usually means the ingredient_nutrients column format is different than expected.")
    print("\nPlease check a few rows manually:")
    print(df[['RecipeName', 'ingredient_nutrients']].head(3))
    exit(1)

# Sort by frequency
ingredient_df = ingredient_df.sort_values('sample_count', ascending=False)

# Save
output_path = 'data/ingredient_nutrition_table.csv'
ingredient_df.to_csv(output_path, index=False)

print(f"\n✅ Saved ingredient table: {output_path}")
print(f"📊 Total ingredients: {len(ingredient_df)}")
print("\n📋 Top 10 most common ingredients:")
print(ingredient_df.head(10).to_string(index=False))

print("\n" + "="*80)
print("✅ INGREDIENT TABLE BUILT SUCCESSFULLY")
print("="*80)

