# File: backend/recipe_recommender.py

import pandas as pd
import numpy as np
from medical_constraints import MEDICAL_CONSTRAINTS


class MedicalAwareRecipeRecommender:
    """
    TIER 2: Medical-Safe Recipe Recommendations with Enhanced Matching
    
    Features:
    - Medical constraint filtering (sodium, carbs, protein limits)
    - Ingredient-based exclusions (avoid harmful foods)
    - LLM preference filtering (cuisines, dislikes, allergies, time)
    - Weighted nutritional scoring (prioritizes protein)
    - Non-food item filtering (spice mixes, pastes)
    - Protein gap analysis and suggestions
    """
    
    # Diet mapping to handle typos and variations in dataset
    DIET_MAPPING = {
        'vegetarian': ['Vegetarian', 'High Protein Vegetarian'],
        'non-vegetarian': ['Non Vegeterian', 'High Protein Non Vegetarian'],  # Note: dataset has typo
        'non vegetarian': ['Non Vegeterian', 'High Protein Non Vegetarian'],
        'vegan': ['Vegan'],
        'eggetarian': ['Eggetarian'],
        'diabetic': ['Diabetic Friendly'],
        'diabetic friendly': ['Diabetic Friendly'],
        'gluten free': ['Gluten Free'],
        'sugar free': ['Sugar Free Diet'],
        'no onion no garlic': ['No Onion No Garlic (Sattvic)'],
    }
    
    def __init__(self, recipes_df):
        """
        Initialize recommender with cleaned recipe database
        
        Args:
            recipes_df: Pandas DataFrame with recipe data
        """
        self.recipes = self._preprocess_recipes(recipes_df)
        # DEBUG: Print dataset info
        print("\n📊 Recipe Dataset Info:")
        print(f"Total recipes: {len(self.recipes)}")
        print(f"Columns: {self.recipes.columns.tolist()}")
        print(f"\nUnique Diets: {self.recipes['Diet'].unique()}")
        print(f"\nUnique Courses: {self.recipes['Course'].unique()}")
        print(f"\nUnique Cuisines: {self.recipes['Cuisine'].unique()[:10]}")  # Show first 10
        print(f"\nSample recipe:")
        print(self.recipes.iloc[0][['RecipeName', 'Course', 'Diet', 'TotalTimeInMins']])
        
    def _preprocess_recipes(self, recipes_df):
        """
        Clean and prepare recipe database
        """
        df = recipes_df.copy()
        
        # Filter out non-food items (spice mixes, pastes, chutneys)
        non_food_keywords = [
            'masala', 'spice mix', 'paste', 'chutney', 'pickle',
            'powder', 'seasoning', 'sauce mix', 'curry powder'
        ]
        
        pattern = '|'.join(non_food_keywords)
        df = df[~df['RecipeName'].str.contains(pattern, case=False, na=False)]
        
        print(f"✓ Filtered out non-food items: {len(recipes_df) - len(df)} recipes removed")
        print(f"✓ Final recipe database: {len(df)} recipes")
        
        return df
    
    def filter_by_medical_constraints(self, recipes_df, medical_conditions):
        """
        Apply hard medical constraints - unsafe recipes are completely excluded
        
        Args:
            recipes_df: DataFrame of recipes to filter
            medical_conditions: List of condition strings (e.g., ['diabetes', 'hypertension'])
        
        Returns:
            Filtered DataFrame with only medically-safe recipes
        """
        filtered = recipes_df.copy()
        
        for condition in medical_conditions:
            if condition not in MEDICAL_CONSTRAINTS:
                continue
            
            constraints = MEDICAL_CONSTRAINTS[condition]
            
            # Sodium limit (hypertension, heart disease, kidney disease)
            if 'max_sodium_per_serving' in constraints:
                limit = constraints['max_sodium_per_serving']
                filtered = filtered[filtered['sodium_per_serving'] <= limit]
            
            # Carbohydrate limit (diabetes)
            if 'max_carbs_per_serving' in constraints:
                limit = constraints['max_carbs_per_serving']
                filtered = filtered[filtered['carbohydrate_per_serving'] <= limit]
            
            # Protein limit (kidney disease)
            if 'max_protein_per_serving' in constraints:
                limit = constraints['max_protein_per_serving']
                filtered = filtered[filtered['protein_per_serving'] <= limit]
            
            # Fat limit (heart disease, high cholesterol)
            if 'max_saturated_fat_per_serving' in constraints:
                # Using total fat as proxy (saturated_fat column not available)
                limit = constraints['max_saturated_fat_per_serving']
                filtered = filtered[filtered['fat_per_serving'] <= limit * 2]
            
            # Required diet (celiac disease = gluten free)
            if 'required_diet' in constraints:
                required_diet = constraints['required_diet']
                filtered = filtered[filtered['Diet'] == required_diet]
            
            # Ingredient exclusions (allergies, intolerances, medical restrictions)
            if 'avoid_ingredients' in constraints:
                avoid_list = constraints['avoid_ingredients']
                for ingredient in avoid_list:
                    filtered = filtered[
                        ~filtered['Ingredients'].str.contains(ingredient, case=False, na=False)
                    ]
        
        return filtered
    
    def filter_by_preferences(self, recipes_df, preferred_cuisines=None, disliked_ingredients=None, allergies=None):
        """
        Apply LLM-parsed user preferences
        
        Args:
            recipes_df: DataFrame of recipes to filter
            preferred_cuisines: List of cuisine names to include (or None for all)
            disliked_ingredients: List of ingredients to exclude
            allergies: List of allergens to strictly exclude
        
        Returns:
            Filtered DataFrame
        """
        filtered = recipes_df.copy()
        
        # Filter by preferred cuisines
        if preferred_cuisines and isinstance(preferred_cuisines, list) and len(preferred_cuisines) > 0:
            print(f"   🍽️  Filtering for cuisines: {preferred_cuisines}")
            filtered = filtered[filtered['Cuisine'].isin(preferred_cuisines)]
            print(f"   After cuisine filtering: {len(filtered)} recipes")
        
        # Exclude disliked ingredients
        if disliked_ingredients and isinstance(disliked_ingredients, list):
            print(f"   🚫 Excluding disliked ingredients: {disliked_ingredients}")
            for ingredient in disliked_ingredients:
                # Check in recipe name and ingredients column
                mask = ~(
                    filtered['RecipeName'].str.contains(ingredient, case=False, na=False) |
                    filtered['Ingredients'].str.contains(ingredient, case=False, na=False)
                )
                filtered = filtered[mask]
            print(f"   After disliked ingredient filtering: {len(filtered)} recipes")
        
        # Exclude allergens (stricter - also check ingredientsname column if exists)
        if allergies and isinstance(allergies, list):
            print(f"   ⚠️  Excluding allergens: {allergies}")
            for allergen in allergies:
                mask = ~(
                    filtered['RecipeName'].str.contains(allergen, case=False, na=False) |
                    filtered['Ingredients'].str.contains(allergen, case=False, na=False)
                )
                # Also check ingredientsname if column exists
                if 'ingredientsname' in filtered.columns:
                    mask = mask & ~filtered['ingredientsname'].str.contains(allergen, case=False, na=False)
                
                filtered = filtered[mask]
            print(f"   After allergen filtering: {len(filtered)} recipes")
        
        return filtered
    
    def calculate_match_score(self, recipe, target):
        """
        Calculate weighted nutritional match score (0-100)
        
        Higher protein weight for elderly and medical conditions
        
        Args:
            recipe: Single recipe row (pandas Series)
            target: Dict with 'calories', 'protein_g', 'carbs_g', 'fat_g'
        
        Returns:
            Float score (0-100, where 100 = perfect match)
        """
        # Prevent division by zero
        target_cal = max(target['calories'], 1)
        target_protein = max(target['protein_g'], 1)
        target_carbs = max(target['carbs_g'], 1)
        target_fat = max(target['fat_g'], 1)
        
        # Calculate percentage differences
        cal_diff = abs(recipe['energy_per_serving'] - target['calories']) / target_cal
        protein_diff = abs(recipe['protein_per_serving'] - target['protein_g']) / target_protein
        carbs_diff = abs(recipe['carbohydrate_per_serving'] - target['carbs_g']) / target_carbs
        fat_diff = abs(recipe['fat_per_serving'] - target['fat_g']) / target_fat
        
        # Cap differences at 2.0 (200% = worst case)
        cal_diff = min(cal_diff, 2.0)
        protein_diff = min(protein_diff, 2.0)
        carbs_diff = min(carbs_diff, 2.0)
        fat_diff = min(fat_diff, 2.0)
        
        # Weighted average (protein prioritized for medical users)
        weighted_diff = (
            cal_diff * 0.30 +       # Calories: 30%
            protein_diff * 0.40 +   # Protein: 40% (MOST IMPORTANT)
            carbs_diff * 0.20 +     # Carbs: 20%
            fat_diff * 0.10         # Fat: 10%
        )
        
        # Convert to 0-100 score (lower diff = higher score)
        score = max(0, 100 - (weighted_diff * 50))
        
        return score
    
    def calculate_preference_bonus(self, recipe, medical_conditions):
        """
        Boost recipes with medically-preferred ingredients
        
        Args:
            recipe: Single recipe row
            medical_conditions: List of conditions
        
        Returns:
            Float bonus (0.0 to 0.20)
        """
        bonus = 0.0
        
        for condition in medical_conditions:
            if condition not in MEDICAL_CONSTRAINTS:
                continue
            
            constraints = MEDICAL_CONSTRAINTS[condition]
            
            if 'preferred_ingredients' in constraints:
                preferred = constraints['preferred_ingredients']
                ingredients_lower = recipe['Ingredients'].lower()
                
                for ingredient in preferred:
                    if ingredient in ingredients_lower:
                        bonus += 0.05  # 5% boost per preferred ingredient
        
        return min(bonus, 0.20)  # Max 20% total bonus
    
    def analyze_protein_gap(self, recipe, target_protein):
        """
        Calculate protein gap and suggest supplements
        
        Args:
            recipe: Single recipe row
            target_protein: Target protein in grams
        
        Returns:
            Dict with gap analysis and suggestions
        """
        gap = target_protein - recipe['protein_per_serving']
        
        if gap <= 2:
            return {
                'gap': gap,
                'status': 'excellent',
                'suggestion': None
            }
        elif gap <= 5:
            return {
                'gap': gap,
                'status': 'good',
                'suggestion': 'Add 1 boiled egg (+6g protein)'
            }
        elif gap <= 10:
            return {
                'gap': gap,
                'status': 'moderate',
                'suggestion': 'Add 50g paneer (+9g protein) or 1 cup Greek yogurt (+15g)'
            }
        else:
            return {
                'gap': gap,
                'status': 'significant',
                'suggestion': f'Add 2 eggs + 50g paneer (+15g protein) or protein shake (+20g)'
            }
    
    def recommend(self, user_targets, medical_conditions=[], preferred_cuisines=None, 
                  disliked_ingredients=None, allergies=None, top_n=10):
        """
        Complete recommendation pipeline with medical safety, LLM preferences, and protein analysis
        
        Args:
            user_targets: Dict with 'course', 'diet', 'max_time', 'calories', 'protein_g', etc.
            medical_conditions: List of medical conditions
            preferred_cuisines: List of cuisine names (from LLM parser)
            disliked_ingredients: List of ingredients to avoid (from LLM parser)
            allergies: List of allergens to exclude (from LLM parser)
            top_n: Number of recommendations to return
        """
        
        # Step 1: Basic filtering (course, diet, time)
        
        # Ensure required columns exist and have no NaN
        required_cols = ['Course', 'Diet', 'TotalTimeInMins']
        filtered = self.recipes.copy()
        
        # Remove rows with missing data in critical columns
        for col in required_cols:
            if col in filtered.columns:
                filtered = filtered[filtered[col].notna()]
        
        print(f"After removing NaN: {len(filtered)} recipes")
        
        # Handle course matching (case-insensitive, flexible for snacks)
        course = user_targets.get('course', 'Breakfast')
        
        # Special handling for snacks (match multiple course types)
        if 'snack' in course.lower():
            course_filter = filtered['Course'].str.contains(
                'Snack|Appetizer|Starter|Side|Dessert', 
                case=False, 
                na=False
            )
        else:
            course_filter = filtered['Course'].str.contains(
                course, 
                case=False, 
                na=False
            )
        
        filtered = filtered[course_filter]
        print(f"After course filtering ({course}): {len(filtered)} recipes")
        
        # Handle diet matching with typo correction
        diet_input = user_targets.get('diet', 'Vegetarian').lower().replace('-', ' ').strip()
        diet_values = self.DIET_MAPPING.get(diet_input)
        
        if diet_values:
            filtered = filtered[filtered['Diet'].isin(diet_values)]
            print(f"After diet filtering (mapped {diet_input} → {diet_values}): {len(filtered)} recipes")
        else:
            filtered = filtered[
                filtered['Diet'].str.contains(user_targets.get('diet', 'Vegetarian'), case=False, na=False)
            ]
            print(f"After diet filtering (fallback - {diet_input}): {len(filtered)} recipes")
        
        # Handle time filtering
        max_time = user_targets.get('max_time', user_targets.get('max_time_mins', 60))
        filtered = filtered[filtered['TotalTimeInMins'] <= max_time]
        print(f"After time filtering (<={max_time}min): {len(filtered)} recipes")
        
        # Step 2: Apply LLM PREFERENCE FILTERS (NEW!)
        filtered = self.filter_by_preferences(
            filtered, 
            preferred_cuisines=preferred_cuisines,
            disliked_ingredients=disliked_ingredients,
            allergies=allergies
        )
        
        if len(filtered) == 0:
            print("⚠️  No recipes after preference filtering, relaxing cuisine constraint...")
            # Retry without cuisine filter
            filtered = self.recipes.copy()
            for col in required_cols:
                if col in filtered.columns:
                    filtered = filtered[filtered[col].notna()]
            
            if 'snack' in course.lower():
                course_filter = filtered['Course'].str.contains('Snack|Appetizer|Starter|Side|Dessert', case=False, na=False)
            else:
                course_filter = filtered['Course'].str.contains(course, case=False, na=False)
            
            filtered = filtered[course_filter]
            
            if diet_values:
                filtered = filtered[filtered['Diet'].isin(diet_values)]
            
            filtered = filtered[filtered['TotalTimeInMins'] <= max_time]
            
            # Retry preferences without cuisine constraint
            filtered = self.filter_by_preferences(
                filtered, 
                preferred_cuisines=None,  # Remove cuisine constraint
                disliked_ingredients=disliked_ingredients,
                allergies=allergies
            )
        
        # Step 3: Apply MEDICAL SAFETY CONSTRAINTS
        if medical_conditions:
            filtered = self.filter_by_medical_constraints(filtered, medical_conditions)
            print(f"After medical filtering: {len(filtered)} recipes")
        
        if len(filtered) == 0:
            print("❌ No recipes found even with relaxed filters")
            return pd.DataFrame()
        
        # Step 4: Calculate match scores
        scores = []
        protein_gaps = []
        suggestions = []
        
        for _, recipe in filtered.iterrows():
            # Base nutritional similarity score
            score = self.calculate_match_score(recipe, user_targets)
            
            # Add medical preference bonus
            if medical_conditions:
                bonus = self.calculate_preference_bonus(recipe, medical_conditions)
                score = score * (1 + bonus)
            
            scores.append(min(score, 100))
            
            # Analyze protein gap
            gap_analysis = self.analyze_protein_gap(recipe, user_targets['protein_g'])
            protein_gaps.append(gap_analysis['gap'])
            suggestions.append(gap_analysis['suggestion'])
        
        filtered['match_score'] = scores
        filtered['protein_gap'] = protein_gaps
        filtered['protein_suggestion'] = suggestions
        
        # Step 5: Rank by match score and return top N
        recommendations = filtered.sort_values('match_score', ascending=False).head(top_n)
        
        return recommendations[[
            'RecipeName', 'Cuisine', 'Diet', 'TotalTimeInMins',
            'energy_per_serving', 'protein_per_serving',
            'carbohydrate_per_serving', 'fat_per_serving',
            'sodium_per_serving', 'match_score', 'protein_gap', 'protein_suggestion'
        ]]
    
    def recommend_with_display(self, user_targets, medical_conditions=[], 
                               preferred_cuisines=None, disliked_ingredients=None, 
                               allergies=None, top_n=5):
        """
        Get recommendations with formatted display output
        
        Returns both DataFrame and formatted string for printing
        """
        recommendations = self.recommend(
            user_targets, medical_conditions, 
            preferred_cuisines, disliked_ingredients, allergies, top_n
        )
        
        if len(recommendations) == 0:
            return recommendations, "No suitable recipes found"
        
        # Format output
        output = []
        output.append("\n" + "=" * 80)
        output.append("RECOMMENDED RECIPES")
        output.append("=" * 80)
        
        for idx, (_, recipe) in enumerate(recommendations.iterrows(), 1):
            output.append(f"\n{idx}. {recipe['RecipeName']}")
            output.append(f"   Cuisine: {recipe['Cuisine']} | Time: {recipe['TotalTimeInMins']:.0f} min")
            output.append(f"   Nutrition: {recipe['energy_per_serving']:.0f} cal | " +
                         f"{recipe['protein_per_serving']:.1f}g P | " +
                         f"{recipe['carbohydrate_per_serving']:.1f}g C | " +
                         f"{recipe['fat_per_serving']:.1f}g F")
            
            if medical_conditions:
                output.append(f"   Sodium: {recipe['sodium_per_serving']:.0f}mg " +
                            f"(SAFE for {', '.join(medical_conditions)})")
            
            output.append(f"   Match Score: {recipe['match_score']:.1f}/100")
            
            # Show protein gap if significant
            if recipe['protein_gap'] > 2:
                output.append(f"   ⚠️  Protein Gap: {recipe['protein_gap']:.1f}g")
                if recipe['protein_suggestion']:
                    output.append(f"   💡 Suggestion: {recipe['protein_suggestion']}")
        
        return recommendations, "\n".join(output)
