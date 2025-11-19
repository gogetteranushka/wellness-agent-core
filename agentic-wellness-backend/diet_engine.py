# File: backend/diet_engine.py

class DietEngine:
    """
    TIER 1: Knowledge-Based Nutrition Calculator
    Uses clinically-validated formulas for BMR/TDEE calculation
    """
    
    def calculate_bmr(self, age, gender, weight_kg, height_cm):
        """
        Mifflin-St Jeor equation (most accurate formula, ±10% error)
        """
        if gender.upper() == 'M':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        return round(bmr, 2)
    
    def calculate_tdee(self, bmr, activity_level):
        """
        Apply activity multipliers based on research
        """
        multipliers = {
            'sedentary': 1.2,           # Desk job, minimal movement
            'lightly_active': 1.375,    # Light exercise 1-3 days/week
            'moderately_active': 1.55,  # Moderate exercise 3-5 days/week
            'very_active': 1.725,       # Hard exercise 6-7 days/week
            'extra_active': 1.9         # Athlete-level training
        }
        
        return round(bmr * multipliers.get(activity_level, 1.2), 2)
    
    def calculate_macros(self, target_calories, goal, medical_conditions=[], diet_type='Vegetarian'):
        """
        Research-based macro distribution with medical adjustments
        """
        # Base macro percentages by goal
        if goal == 'weight_loss':
            if diet_type in ['Vegetarian', 'Vegan']:
                protein_pct = 0.20  # Realistic for Indian veg
                carbs_pct = 0.50
                fat_pct = 0.30
            else:
                protein_pct = 0.30
                carbs_pct = 0.40
                fat_pct = 0.30
        
        elif goal == 'muscle_gain':
            if diet_type in ['Vegetarian', 'Vegan']:
                protein_pct = 0.25
                carbs_pct = 0.50
                fat_pct = 0.25
            else:
                protein_pct = 0.35
                carbs_pct = 0.45
                fat_pct = 0.20
        
        else:  # maintenance
            protein_pct = 0.20
            carbs_pct = 0.50
            fat_pct = 0.30
        
        # Medical adjustments
        if 'diabetes' in medical_conditions or 'pre_diabetes' in medical_conditions:
            carbs_pct -= 0.10
            fat_pct += 0.10  # Compensate with healthy fats
        
        if 'kidney_disease' in medical_conditions:
            protein_pct -= 0.10
            carbs_pct += 0.10
        
        if 'heart_disease' in medical_conditions or 'high_cholesterol' in medical_conditions:
            fat_pct -= 0.05
            carbs_pct += 0.05
        
        # Ensure percentages sum to 100%
        total_pct = protein_pct + carbs_pct + fat_pct
        if abs(total_pct - 1.0) > 0.01:  # If not summing to 100%
            # Adjust carbs to make it exactly 100%
            carbs_pct = 1.0 - protein_pct - fat_pct
        
        # Calculate grams (protein/carbs = 4 cal/g, fat = 9 cal/g)
        protein_g = round((target_calories * protein_pct) / 4)
        carbs_g = round((target_calories * carbs_pct) / 4)
        fat_g = round((target_calories * fat_pct) / 9)
        
        return {
            'protein_g': protein_g,
            'carbs_g': carbs_g,
            'fat_g': fat_g,
            'protein_percent': int(protein_pct * 100),
            'carbs_percent': int(carbs_pct * 100),
            'fat_percent': int(fat_pct * 100)
        }
    
    def generate_personalized_plan(self, user_profile):
        """
        Complete TIER 1 pipeline
        
        Args:
            user_profile: {
                'age': 25,
                'gender': 'M',
                'weight_kg': 75,
                'height_cm': 175,
                'activity_level': 'moderately_active',
                'goal': 'weight_loss',  # 'weight_loss', 'muscle_gain', 'maintenance'
                'medical_conditions': ['diabetes'],
                'diet_type': 'Vegetarian'  # Optional, defaults to 'Vegetarian'
            }
        
        Returns:
            Complete nutrition plan with TDEE, targets, and meal breakdown
        """
        # Step 1: Calculate BMR
        bmr = self.calculate_bmr(
            user_profile['age'],
            user_profile['gender'],
            user_profile['weight_kg'],
            user_profile['height_cm']
        )
        
        # Step 2: Calculate TDEE
        tdee = self.calculate_tdee(bmr, user_profile['activity_level'])
        
        # Step 3: Apply goal adjustment
        if user_profile['goal'] == 'weight_loss':
            target_calories = tdee - 500  # 1 lb/week loss
        elif user_profile['goal'] == 'muscle_gain':
            target_calories = tdee + 300  # 0.5 lb/week gain
        else:
            target_calories = tdee
        
        # Step 4: Apply safety minimums
        if user_profile['gender'].upper() == 'F':
            target_calories = max(1200, target_calories)
        else:
            target_calories = max(1500, target_calories)
        
        target_calories = round(target_calories)
        
        # Step 5: Calculate macros
        macros = self.calculate_macros(
            target_calories,
            user_profile['goal'],
            user_profile.get('medical_conditions', []),
            user_profile.get('diet_type', 'Vegetarian')  # Default to Vegetarian if not specified
        )
        
        # Step 6: Meal breakdown (25% breakfast, 35% lunch, 30% dinner, 10% snacks)
        meal_breakdown = {
            'breakfast': {
                'calories': round(target_calories * 0.25),
                'protein_g': round(macros['protein_g'] * 0.25),
                'carbs_g': round(macros['carbs_g'] * 0.25),
                'fat_g': round(macros['fat_g'] * 0.25)
            },
            'lunch': {
                'calories': round(target_calories * 0.35),
                'protein_g': round(macros['protein_g'] * 0.35),
                'carbs_g': round(macros['carbs_g'] * 0.35),
                'fat_g': round(macros['fat_g'] * 0.35)
            },
            'dinner': {
                'calories': round(target_calories * 0.30),
                'protein_g': round(macros['protein_g'] * 0.30),
                'carbs_g': round(macros['carbs_g'] * 0.30),
                'fat_g': round(macros['fat_g'] * 0.30)
            },
            'snacks': {
                'calories': round(target_calories * 0.10),
                'protein_g': round(macros['protein_g'] * 0.10),
                'carbs_g': round(macros['carbs_g'] * 0.10),
                'fat_g': round(macros['fat_g'] * 0.10)
            }
        }
        
        return {
            'bmr': bmr,
            'tdee': tdee,
            'target_calories': target_calories,
            'daily_macros': macros,
            'meal_breakdown': meal_breakdown,
            'goal': user_profile['goal']
        }
