# File: explore_nutrition_data.py

import pandas as pd
import numpy as np

# Load your recipe dataset
df = pd.read_csv('data/recipe_nutrients_cleaned.csv')


# 1. How many recipes do we have?
print(df.shape())

# 2. What columns contain the INPUTS (ingredients)?
print(df['TranslatedIngredients'])

# 3. What columns contain the OUTPUTS (nutrition to predict)?
# List all 5 nutrition targets
print(df['energy_per_serving', 'protein_per_serving', 'fat_per_serving', 'carbohydrate_per_serving', 'sodium_per_serving' ])

# 4. Show the first 3 recipes with their ingredients and calories

print("Sample recipes:")
print(df[['Ingredients', 'energy_per_serving']].head(3))

# 5. Check for missing values in 'Ingredients' column
missing_count = df.isnull().sum()
print("Missing ingredients:", missing-count) 

# 6. What's the average calories per recipe?
avg_calories = np.mean(df['energy_per_serving'])
print(f"Average calories: {avg_calories:.2f}")

# 7. What's the range of protein values?
min_protein = np.min(protein_per_serving)
max_protein = np.max(protein_per_serving)
print(f"Protein range: {min_protein:.2f}g to {max_protein:.2f}g")
