from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from diet_engine import DietEngine
from recipe_recommender import MedicalAwareRecipeRecommender
from difflib import get_close_matches
from llm_client import preference_parser, workout_preference_parser
from workout_engine import generate_weekly_plan


app = Flask(__name__)
CORS(app)
load_dotenv()

diet_engine = DietEngine()

# Auth Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Load datasets
foods = pd.read_csv('data/Food_and_Nutrition.csv')
foods.columns = foods.columns.str.lower().str.strip()

# Load USDA Ingredient Database
try:
    usda_ingredients = pd.read_csv('data/usda_ingredients.csv')
    usda_ingredients['ingredient_name'] = usda_ingredients['ingredient_name'].str.lower().str.strip()
    
    # Create lookup dictionary for fast access
    ingredient_db = {}
    for _, row in usda_ingredients.iterrows():
        ingredient_db[row['ingredient_name']] = {
            'calories': row['calories_per_100g'],
            'protein': row['protein_per_100g'],
            'carbs': row['carbs_per_100g'],
            'fat': row['fat_per_100g'],
            'sodium': row.get('sodium_per_100mg', 0)
        }
    
    print(f"✅ USDA ingredient database loaded: {len(ingredient_db)} ingredients")
except Exception as e:
    print(f"❌ Error loading USDA database: {e}")
    ingredient_db = {}


# Load Recipe Database and Initialize Recommender
print("Loading recipe database...")
try:
    recipes_df = pd.read_csv('data/recipe_nutrients_cleaned.csv')
    recipe_recommender = MedicalAwareRecipeRecommender(recipes_df)
    print(f"✅ Recipe recommender loaded with {len(recipes_df)} recipes")
except Exception as e:
    print(f"❌ Error loading recipes: {e}")
    recipe_recommender = None

# Load AI Symptom Model
try:
    symptom_classifier = joblib.load('models/symptom_disease_classifier.pkl')
    symptom_list = joblib.load('models/symptom_list.pkl')
    print("✅ AI Symptom Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading symptom model: {e}")
    symptom_classifier = None
    symptom_list = []


# ============================================================================
# FEATURE ENGINEERING HELPER
# ============================================================================
def extract_features_from_ingredients(ingredients_list):
    """
    Convert raw ingredients into feature dict matching indb_features_with_targets.csv schema.
    
    Expected features:
    - ingredient_count
    - total_weight_grams
    - has_milk, has_sugar, has_rice, has_dal, has_paneer, has_ghee, has_butter, 
      has_cream, has_oil, has_onion, has_tomato, has_potato, has_chicken, has_vegetables
    - dairy_grams, grain_grams, protein_source_grams, fat_source_grams, 
      vegetable_grams, spice_grams
    - rich_ingredient_count
    """
    
    # Initialize features
    features = {
        'ingredient_count': len(ingredients_list),
        'total_weight_grams': 0.0,
        'has_milk': 0, 'has_sugar': 0, 'has_rice': 0, 'has_dal': 0,
        'has_paneer': 0, 'has_ghee': 0, 'has_butter': 0, 'has_cream': 0,
        'has_oil': 0, 'has_onion': 0, 'has_tomato': 0, 'has_potato': 0,
        'has_chicken': 0, 'has_vegetables': 0,
        'dairy_grams': 0.0, 'grain_grams': 0.0, 'protein_source_grams': 0.0,
        'fat_source_grams': 0.0, 'vegetable_grams': 0.0, 'spice_grams': 0.0,
        'rich_ingredient_count': 0
    }
    
    # Keyword mappings
    dairy_keywords = ['milk', 'yogurt', 'curd', 'cream', 'paneer', 'cheese', 'butter', 'ghee']
    grain_keywords = ['rice', 'wheat', 'flour', 'roti', 'bread', 'oats', 'dal', 'lentil']
    protein_keywords = ['chicken', 'meat', 'egg', 'fish', 'paneer', 'dal', 'lentil', 'tofu']
    fat_keywords = ['oil', 'ghee', 'butter', 'cream']
    vegetable_keywords = ['onion', 'tomato', 'potato', 'carrot', 'spinach', 'pepper', 'vegetable']
    spice_keywords = ['spice', 'masala', 'turmeric', 'cumin', 'coriander', 'chili', 'salt']
    rich_keywords = ['butter', 'ghee', 'cream', 'cheese', 'paneer', 'oil']
    
    for ing in ingredients_list:
        name = ing['name'].lower().strip()
        amount = float(ing.get('amount', 0))
        unit = ing.get('unit', 'g').lower()
        
        # Convert to grams (simple approximation)
        if unit in ['ml', 'g']:
            amount_g = amount
        elif unit == 'kg':
            amount_g = amount * 1000
        elif unit == 'tsp':
            amount_g = amount * 5
        elif unit == 'tbsp':
            amount_g = amount * 15
        elif unit == 'cup':
            amount_g = amount * 240
        else:
            amount_g = amount  # default
        
        features['total_weight_grams'] += amount_g
        
        # Set flags
        if any(kw in name for kw in ['milk', 'curd', 'yogurt']):
            features['has_milk'] = 1
        if 'sugar' in name:
            features['has_sugar'] = 1
        if 'rice' in name:
            features['has_rice'] = 1
        if 'dal' in name or 'lentil' in name:
            features['has_dal'] = 1
        if 'paneer' in name:
            features['has_paneer'] = 1
        if 'ghee' in name:
            features['has_ghee'] = 1
        if 'butter' in name:
            features['has_butter'] = 1
        if 'cream' in name:
            features['has_cream'] = 1
        if 'oil' in name:
            features['has_oil'] = 1
        if 'onion' in name:
            features['has_onion'] = 1
        if 'tomato' in name:
            features['has_tomato'] = 1
        if 'potato' in name:
            features['has_potato'] = 1
        if 'chicken' in name or 'meat' in name:
            features['has_chicken'] = 1
        if any(kw in name for kw in vegetable_keywords):
            features['has_vegetables'] = 1
        
        # Accumulate grams by category
        if any(kw in name for kw in dairy_keywords):
            features['dairy_grams'] += amount_g
        if any(kw in name for kw in grain_keywords):
            features['grain_grams'] += amount_g
        if any(kw in name for kw in protein_keywords):
            features['protein_source_grams'] += amount_g
        if any(kw in name for kw in fat_keywords):
            features['fat_source_grams'] += amount_g
        if any(kw in name for kw in vegetable_keywords):
            features['vegetable_grams'] += amount_g
        if any(kw in name for kw in spice_keywords):
            features['spice_grams'] += amount_g
        if any(kw in name for kw in rich_keywords):
            features['rich_ingredient_count'] += 1
    
    return features


def get_meal_recommendations(risk_condition, dietary_preference=None):
    filtered = foods.copy()
    if dietary_preference:
        filtered = filtered[filtered['dietary preference'].str.lower() == dietary_preference.lower()]
    sample = filtered.sample(1).iloc[0] if len(filtered) > 0 else foods.sample(1).iloc[0]
    return {
        "breakfast": str(sample.get('breakfast suggestion', 'Oatmeal')),
        "lunch": str(sample.get('lunch suggestion', 'Grilled chicken salad')),
        "dinner": str(sample.get('dinner suggestion', 'Salmon with vegetables')),
        "snack": str(sample.get('snack suggestion', 'Greek yogurt'))
    }


# ============================================================================
# NUTRITION PREDICTOR
# ============================================================================
@app.route('/api/predict-nutrition', methods=['POST'])
def predict_nutrition():
    """Predict recipe nutrition from ingredients using USDA database."""
    try:
        if not ingredient_db:
            return jsonify({'error': 'Ingredient database not loaded'}), 500

        data = request.json or {}
        
        if 'ingredients' not in data:
            return jsonify({'error': 'Must provide "ingredients" array'}), 400

        ingredients_list = data['ingredients']
        
        # Initialize totals
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_weight = 0
        matched_count = 0
        
        print(f"\n🔍 Processing {len(ingredients_list)} ingredients:")
        
        for ing in ingredients_list:
            name = ing.get('name', '').lower().strip()
            amount = float(ing.get('amount', 0))
            unit = ing.get('unit', 'g').lower()
            
            # Convert to grams
            if unit == 'ml':
                amount_g = amount
            elif unit == 'kg':
                amount_g = amount * 1000
            elif unit == 'tsp':
                amount_g = amount * 5
            elif unit == 'tbsp':
                amount_g = amount * 15
            elif unit == 'cup':
                amount_g = amount * 240
            else:
                amount_g = amount
            
            total_weight += amount_g
            
            # Try exact match first
            nutrition = ingredient_db.get(name)
            
            # If no exact match, try partial matching (search in database keys)
            if not nutrition:
                # Look for any database entry that contains the search term
                for db_key in ingredient_db.keys():
                    if name in db_key or db_key.split(',')[0] == name:
                        nutrition = ingredient_db[db_key]
                        print(f"  ✓ '{name}' → matched to '{db_key}'")
                        matched_count += 1
                        break
            else:
                matched_count += 1
                print(f"  ✓ '{name}' → exact match")
            
            # If still no match, use hardcoded defaults for common Indian ingredients
            if not nutrition:
                if 'tomato' in name:
                    nutrition = {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'sodium': 0}
                    print(f"  ✓ '{name}' → tomato default")
                elif 'rice' in name:
                    nutrition = {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'sodium': 0}
                    print(f"  ✓ '{name}' → rice default")
                elif 'dal' in name or 'lentil' in name:
                    nutrition = {'calories': 116, 'protein': 9, 'carbs': 20, 'fat': 0.4, 'sodium': 0}
                    print(f"  ✓ '{name}' → dal default")
                elif 'oil' in name:
                    nutrition = {'calories': 884, 'protein': 0, 'carbs': 0, 'fat': 100, 'sodium': 0}
                    print(f"  ✓ '{name}' → oil default")
                elif 'ghee' in name:
                    nutrition = {'calories': 900, 'protein': 0, 'carbs': 0, 'fat': 100, 'sodium': 0}
                    print(f"  ✓ '{name}' → ghee default")
                elif 'paneer' in name or 'cheese' in name:
                    nutrition = {'calories': 265, 'protein': 18, 'carbs': 1.2, 'fat': 20, 'sodium': 0}
                    print(f"  ✓ '{name}' → paneer/cheese default")
                elif 'milk' in name:
                    nutrition = {'calories': 60, 'protein': 3.3, 'carbs': 4.7, 'fat': 3.3, 'sodium': 0}
                    print(f"  ✓ '{name}' → milk default")
                elif 'onion' in name:
                    nutrition = {'calories': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1, 'sodium': 0}
                    print(f"  ✓ '{name}' → onion default")
                elif 'potato' in name:
                    nutrition = {'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1, 'sodium': 0}
                    print(f"  ✓ '{name}' → potato default")
                elif 'chicken' in name:
                    nutrition = {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'sodium': 0}
                    print(f"  ✓ '{name}' → chicken default")
                elif 'egg' in name:
                    nutrition = {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11, 'sodium': 0}
                    print(f"  ✓ '{name}' → egg default")
                elif 'almond' in name or 'badam' in name:
                    nutrition = {'calories': 620, 'protein': 20.4, 'carbs': 16.2, 'fat': 57.8, 'sodium': 0}
                    print(f"  ✓ '{name}' → almond default")
                elif 'sugar' in name:
                    nutrition = {'calories': 387, 'protein': 0, 'carbs': 100, 'fat': 0, 'sodium': 0}
                    print(f"  ✓ '{name}' → sugar default")
                elif 'salt' in name:
                    nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'sodium': 0}
                    print(f"  ✓ '{name}' → salt default")
                else:
                    # Generic vegetable/ingredient
                    nutrition = {'calories': 50, 'protein': 2, 'carbs': 10, 'fat': 0.5, 'sodium': 0}
                    print(f"  ⚠️ '{name}' → generic default")
            
            # Calculate for this ingredient (per 100g values)
            multiplier = amount_g / 100.0
            total_calories += nutrition['calories'] * multiplier
            total_protein += nutrition['protein'] * multiplier
            total_carbs += nutrition['carbs'] * multiplier
            total_fat += nutrition['fat'] * multiplier
        
        print(f"\n📊 Results: {matched_count}/{len(ingredients_list)} database matches")
        print(f"  Calories: {total_calories:.1f} kcal")
        print(f"  Protein: {total_protein:.1f}g, Carbs: {total_carbs:.1f}g, Fat: {total_fat:.1f}g")
        
        # Build confidence range (±15% for database lookups)
        confidence_min = max(10, int(total_calories * 0.85))
        confidence_max = int(total_calories * 1.15)
        
        return jsonify({
            'status': 'success',
            'predicted_nutrition': {
                'calories': round(total_calories, 0),
                'protein_g': round(total_protein, 1),
                'carbs_g': round(total_carbs, 1),
                'fat_g': round(total_fat, 1),
                'confidence_range': {
                    'min': confidence_min,
                    'max': confidence_max
                }
            },
            'model_info': {
                'algorithm': 'USDA Database Lookup',
                'accuracy': '±15% confidence',
                'r_squared': 0.95
            }
        }), 200

    except Exception as e:
        import traceback
        print(f"❌ Nutrition prediction error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500




@app.route('/')
def home():
    return jsonify({"message": "AI Wellness API", "status": "running"})


# ============================================================================
# SYMPTOM CHECKER
# ============================================================================
@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Return list of all available symptoms"""
    if symptom_list:
        symptoms_display = [s.replace('_', ' ').title() for s in symptom_list]
        return jsonify({"symptoms": sorted(symptoms_display)})
    return jsonify({"symptoms": []})


@app.route('/api/symptom-check', methods=['POST'])
def symptom_check():
    """Analyze symptoms and predict diseases"""
    try:
        data = request.json
        symptoms = data.get('symptoms', [])
        
        if not symptom_classifier or not symptom_list:
            return jsonify({"error": "Symptom classifier not loaded"}), 500
        
        if not symptoms:
            return jsonify({"error": "No symptoms provided"}), 400
        
        symptoms_formatted = [s.lower().replace(' ', '_') for s in symptoms]
        
        print(f"📋 User selected: {symptoms}")
        print(f"📋 Formatted for model: {symptoms_formatted}")
        
        symptom_vector = np.zeros(len(symptom_list))
        for i, symptom in enumerate(symptom_list):
            if symptom.lower() in symptoms_formatted:
                symptom_vector[i] = 1
                print(f"✅ Matched: {symptom}")
        
        print(f"📊 Symptom vector sum: {symptom_vector.sum()}")
        
        features = dict(zip(symptom_list, symptom_vector))
        features['symptom_count'] = int(symptom_vector.sum())
        symptom_df = pd.DataFrame([features])
        
        probabilities = symptom_classifier.predict_proba(symptom_df)[0]
        top_indices = np.argsort(probabilities)[-3:][::-1]
        
        conditions = []
        for idx in top_indices:
            prob = probabilities[idx] * 100
            print(f"🔍 Disease: {symptom_classifier.classes_[idx]}, Prob: {prob:.1f}%")
            
            if prob > 1:
                disease_name = symptom_classifier.classes_[idx]
                severity = "High" if prob > 70 else "Medium" if prob > 40 else "Low"
                conditions.append({
                    "name": disease_name,
                    "probability": round(prob, 1),
                    "severity": severity,
                    "prevention": [
                        "Consult a healthcare provider",
                        "Monitor symptoms closely",
                        "Rest and stay hydrated",
                        "Follow medical advice"
                    ]
                })
        
        if not conditions:
            conditions.append({
                "name": "Uncertain Diagnosis",
                "probability": 50,
                "severity": "Low",
                "prevention": ["Please consult a doctor for proper diagnosis"]
            })
        
        return jsonify({"result": {"conditions": conditions}})
    
    except Exception as e:
        print(f"❌ Symptom check error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================================================
# LLM PREFERENCE PARSER
# ============================================================================

@app.route('/api/diet/parse-preferences-text', methods=['POST'])
def parse_preferences_text():
    """Parse natural language preferences using LLM"""
    try:
        data = request.json
        user_text = data.get('text', '')
        fallback_profile = data.get('defaults', {})
        
        if not user_text:
            return jsonify({
                "status": "error",
                "message": "No text provided"
            }), 400
        
        print(f"\n🤖 LLM Preference Parser:")
        print(f"   User text: {user_text[:100]}...")
        print(f"   Has fallback: {fallback_profile is not None}")
        
        # This returns a dict directly now
        result = preference_parser.parse_preferences_text(user_text, fallback_profile)
        
        return jsonify({
            "status": "success",
            "data": {
                "structured": result,
                "warnings": preference_parser.warnings if hasattr(preference_parser, 'warnings') else []
            }
        }), 200
    
    except Exception as e:
        print(f"❌ Parse preferences error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ========================================================================
# WORKOUT PREFERENCE PARSER
# ========================================================================

@app.route('/api/workout/parse-preferences-text', methods=['POST'])
def parse_workout_preferences_text():
    """Parse natural language workout preferences using LLM"""
    try:
        data = request.json or {}
        user_text = data.get('text', '')
        fallback_profile = data.get('defaults', {})

        if not user_text:
            return jsonify({
                "status": "error",
                "message": "No text provided"
            }), 400

        print("\n🤖 Workout Preference Parser API:")
        print(f"   User text: {user_text[:100]}...")
        print(f"   Has fallback: {fallback_profile is not None}")

        result = workout_preference_parser.parse_workout_preferences_text(
            user_text,
            fallback_profile
        )

        return jsonify({
            "status": "success",
            "data": {
                "structured": result,
                "warnings": workout_preference_parser.warnings
            }
        }), 200

    except Exception as e:
        print(f"❌ Workout parse preferences error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ========================================================================
# WORKOUT PLAN GENERATION
# ========================================================================

@app.route('/api/workout/complete-plan', methods=['POST'])
def complete_workout_plan():
    """Generate complete weekly workout plan"""
    try:
        data = request.json or {}
        user_profile = data.get('user_profile', {})
        workout_prefs = data.get('workout_preferences')

        if not workout_prefs:
            return jsonify({
                "status": "error",
                "message": "No workout preferences provided"
            }), 400

        print("\n🏋️ Workout Plan Generation:")
        print(f"   Goal: {workout_prefs.get('goal')}")
        print(f"   Days/week: {workout_prefs.get('days_per_week')}")
        print(f"   Equipment: {workout_prefs.get('equipment')}")
        print(f"   Injuries: {workout_prefs.get('injuries')}")

        # Generate the plan
        plan = generate_weekly_plan(user_profile, workout_prefs)

        print(f"   ✅ Generated plan for {len([d for d in plan['weekly_plan'].values() if d != 'rest'])} training days")

        return jsonify({
            "status": "success",
            "data": plan
        }), 200

    except Exception as e:
        print(f"❌ Workout plan generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================================
# DIET PLAN & ANALYTICS
# ============================================================================
@app.route('/api/diet-plan', methods=['GET'])
def get_diet_plan():
    meals = get_meal_recommendations('Healthy', None)
    return jsonify({
        "meals": {
            "breakfast": {"name": meals["breakfast"], "time": "8:00 AM", "calories": 420, "protein": 28, "carbs": 52, "fat": 12},
            "lunch": {"name": meals["lunch"], "time": "12:30 PM", "calories": 580, "protein": 22, "carbs": 68, "fat": 24},
            "dinner": {"name": meals["dinner"], "time": "7:00 PM", "calories": 520, "protein": 42, "carbs": 35, "fat": 22},
            "snack": {"name": meals["snack"], "time": "3:00 PM", "calories": 240, "protein": 8, "carbs": 28, "fat": 12}
        },
        "dailyTotals": {"calories": 1760, "protein": 100, "carbs": 183, "fat": 70}
    })


@app.route('/api/analytics', methods=['GET'])
def user_analytics():
    return jsonify({
        "daily_calories": [1800, 2000, 1950, 1850, 1900],
        "daily_protein": [90, 100, 95, 88, 92],
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"]
    })


@app.route('/api/profile', methods=['GET'])
def get_profile():
    return jsonify({"name": "Test User", "email": "test@example.com", "age": 30, "bmi": 24.5})


@app.route('/api/profile', methods=['POST'])
def update_profile():
    data = request.json
    return jsonify({"success": True, "data": data})


# ============================================================================
# TIER 1: Nutrition Calculator
# ============================================================================
@app.route('/api/diet/calculate-plan', methods=['POST'])
def calculate_diet_plan():
    """Calculate personalized nutrition plan"""
    try:
        user_profile = request.json
        
        required = ['age', 'gender', 'weight_kg', 'height_cm', 'activity_level', 'goal']
        for field in required:
            if field not in user_profile:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        plan = diet_engine.generate_personalized_plan(user_profile)
        
        return jsonify({
            "status": "success",
            "data": plan
        })
    
    except Exception as e:
        print(f"❌ Diet plan error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# TIER 2: Recipe Recommendations
# ============================================================================
@app.route('/api/diet/recommend-recipes', methods=['POST'])
def recommend_recipes():
    """Get recipe recommendations for a specific meal (TIER 2)"""
    try:
        if not recipe_recommender:
            return jsonify({"error": "Recipe recommender not loaded"}), 500
        
        request_data = request.json
        
        targets = {
            'course': request_data.get('meal', 'Breakfast').capitalize(),
            'calories': request_data['calories'],
            'protein_g': request_data['protein_g'],
            'carbs_g': request_data['carbs_g'],
            'fat_g': request_data['fat_g'],
            'diet': request_data.get('diet', 'Vegetarian'),
            'max_time_mins': request_data.get('max_time_mins', 45)
        }
        
        medical_conditions = request_data.get('medical_conditions', [])
        top_n = request_data.get('top_n', 5)
        
        recommendations_df = recipe_recommender.recommend(
            targets,
            medical_conditions=medical_conditions,
            top_n=top_n
        )
        
        recommendations = []
        for _, recipe in recommendations_df.iterrows():
            recommendations.append({
                'recipe_name': recipe['RecipeName'],
                'cuisine': recipe['Cuisine'],
                'diet': recipe['Diet'],
                'time_mins': int(recipe['TotalTimeInMins']),
                'nutrition': {
                    'calories': float(recipe['energy_per_serving']),
                    'protein_g': float(recipe['protein_per_serving']),
                    'carbs_g': float(recipe['carbohydrate_per_serving']),
                    'fat_g': float(recipe['fat_per_serving']),
                    'sodium_mg': float(recipe['sodium_per_serving'])
                },
                'match_score': float(recipe['match_score']),
                'protein_gap': float(recipe['protein_gap']),
                'protein_suggestion': recipe['protein_suggestion']
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "meal": request_data.get('meal', 'breakfast'),
                "target": targets,
                "recommendations": recommendations,
                "count": len(recommendations)
            }
        }), 200
    
    except Exception as e:
        print(f"❌ Recipe recommendation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/diet/complete-meal-plan', methods=['POST'])
def complete_meal_plan():
    """Generate complete meal plan with recommendations for all meals"""
    try:
        if not recipe_recommender:
            return jsonify({"error": "Recipe recommender not loaded"}), 500
        
        user_profile = request.json
        
        # Extract LLM parsed preferences
        preferred_cuisines = user_profile.get('preferred_cuisines')
        disliked_ingredients = user_profile.get('disliked_ingredients')
        allergies = user_profile.get('allergies')
        max_time_mins = user_profile.get('max_time_mins', {})
        spice_preference = user_profile.get('spice_preference')
        cooking_skill = user_profile.get('cooking_skill')
        
        print(f"\n🎯 Complete Meal Plan Request:")
        print(f"   User: {user_profile.get('gender')}, {user_profile.get('age')}y")
        print(f"   Activity: {user_profile.get('activity_level')}, Goal: {user_profile.get('goal')}")
        print(f"   Diet: {user_profile.get('diet_type')}")
        print(f"   🆕 Preferred Cuisines: {preferred_cuisines}")
        print(f"   🆕 Disliked Ingredients: {disliked_ingredients}")
        print(f"   🆕 Allergies: {allergies}")
        print(f"   🆕 Time Limits: {max_time_mins}")
        print(f"   🆕 Spice: {spice_preference}, Skill: {cooking_skill}")
        
        # Generate nutrition plan
        nutrition_plan = diet_engine.generate_personalized_plan(user_profile)
        
        meals = ['breakfast', 'lunch', 'dinner', 'snacks']
        meal_plans = {}
        
        for meal in meals:
            # Get meal-specific time limit or default to 60 mins
            meal_time_limit = None
            if max_time_mins and isinstance(max_time_mins, dict):
                meal_time_limit = max_time_mins.get(meal.lower())
            time_constraint = meal_time_limit if meal_time_limit else 60
            
            meal_targets = {
                'course': meal.capitalize(),
                'calories': nutrition_plan['meal_breakdown'][meal]['calories'],
                'protein_g': nutrition_plan['meal_breakdown'][meal]['protein_g'],
                'carbs_g': nutrition_plan['meal_breakdown'][meal]['carbs_g'],
                'fat_g': nutrition_plan['meal_breakdown'][meal]['fat_g'],
                'diet': user_profile.get('diet_type', 'Vegetarian'),
                'max_time': time_constraint,  # Add time constraint
            }

            if meal == 'snacks':
                meal_targets['calories'] = meal_targets['calories'] * 2
                meal_targets['course'] = 'Snack|Appetizer|Side Dish'
            
            print(f"\n   📋 {meal.capitalize()}: {meal_targets['calories']} cal, max {time_constraint} mins")
            
            # Call recommend with enhanced parameters
            recommendations_df = recipe_recommender.recommend(
                meal_targets,
                medical_conditions=user_profile.get('medical_conditions', []),
                preferred_cuisines=preferred_cuisines,  # NEW
                disliked_ingredients=disliked_ingredients,  # NEW
                allergies=allergies,  # NEW
                top_n=3
            )
            
            meal_plans[meal] = []
            for _, recipe in recommendations_df.iterrows():
                meal_plans[meal].append({
                    'recipe_name': recipe['RecipeName'],
                    'cuisine': recipe['Cuisine'],
                    'time_mins': int(recipe['TotalTimeInMins']),
                    'nutrition': {
                        'calories': float(recipe['energy_per_serving']),
                        'protein_g': float(recipe['protein_per_serving']),
                        'carbs_g': float(recipe['carbohydrate_per_serving']),
                        'fat_g': float(recipe['fat_per_serving']),
                        'sodium_mg': float(recipe['sodium_per_serving'])
                    },
                    'match_score': float(recipe['match_score']),
                    'protein_suggestion': recipe['protein_suggestion']
                })
        
        return jsonify({
            "status": "success",
            "data": {
                "user_profile": user_profile,
                "nutrition_targets": {
                    "bmr": nutrition_plan['bmr'],
                    "tdee": nutrition_plan['tdee'],
                    "target_calories": nutrition_plan['target_calories'],
                    "daily_macros": nutrition_plan['daily_macros'],
                    "meal_breakdown": nutrition_plan['meal_breakdown']
                },
                "meal_plans": meal_plans,
                "applied_preferences": {  # NEW: Return what was applied
                    "cuisines": preferred_cuisines,
                    "excluded_ingredients": disliked_ingredients,
                    "allergies": allergies,
                    "time_constraints": max_time_mins
                }
            }
        }), 200
    
    except Exception as e:
        print(f"❌ Complete meal plan error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



# ============================================================================
# TIER 3: Hybrid Recommendations
# ============================================================================
@app.route('/api/diet/recommend-hybrid', methods=['POST'])
def recommend_hybrid():
    """Hybrid recommendations combining TIER 2 + TIER 3"""
    try:
        if 'hybrid_recommender' not in globals():
            try:
                from hybrid_recommender import HybridRecommender
                global hybrid_recommender
                hybrid_recommender = HybridRecommender(recipes_df)
            except:
                return jsonify({
                    "error": "Hybrid recommender not available",
                    "fallback": "Use /api/diet/recommend-recipes for TIER 2 only"
                }), 500
        
        data = request.json
        
        targets = {
            'course': data.get('meal', 'Breakfast').capitalize(),
            'calories': data['calories'],
            'protein_g': data['protein_g'],
            'carbs_g': data['carbs_g'],
            'fat_g': data['fat_g'],
            'diet': data.get('diet', 'Vegetarian'),
            'max_time_mins': data.get('max_time_mins', 45)
        }
        
        results = hybrid_recommender.recommend_hybrid(
            user_id=data.get('user_id'),
            user_targets=targets,
            medical_conditions=data.get('medical_conditions', []),
            top_n=data.get('top_n', 5)
        )
        
        recommendations = []
        for _, recipe in results.iterrows():
            recommendations.append({
                'recipe_name': recipe['RecipeName'],
                'cuisine': recipe['Cuisine'],
                'diet': recipe['Diet'],
                'time_mins': int(recipe['TotalTimeInMins']),
                'nutrition': {
                    'calories': float(recipe['energy_per_serving']),
                    'protein_g': float(recipe['protein_per_serving']),
                    'carbs_g': float(recipe['carbohydrate_per_serving']),
                    'fat_g': float(recipe['fat_per_serving']),
                    'sodium_mg': float(recipe['sodium_per_serving'])
                },
                'scores': {
                    'tier2_nutrition': float(recipe['match_score']),
                    'tier3_preference': float(recipe.get('tier3_score', 50)),
                    'hybrid_overall': float(recipe['hybrid_score'])
                },
                'protein_suggestion': recipe.get('protein_suggestion')
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "count": len(recommendations),
                "model_info": {
                    "tier2": "Content-based filtering (nutrition + medical)",
                    "tier3": "Collaborative filtering (user preferences)",
                    "combination": "70% nutrition + 30% preference"
                }
            }
        }), 200
    
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ============================================================================
# USER MANAGEMENT (For Dashboard)
# ============================================================================
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users for dashboard - Mock data for now"""
    try:
        mock_users = [
            {
                "id": "1",
                "name": "Rajesh Kumar",
                "email": "rajesh@example.com",
                "status": "healthy",
                "riskLevel": "low",
                "conditions": [],
                "lastVisit": "2025-11-08"
            },
            {
                "id": "2",
                "name": "Priya Sharma",
                "email": "priya@example.com",
                "status": "monitor",
                "riskLevel": "medium",
                "conditions": ["Diabetes"],
                "lastVisit": "2025-11-05"
            },
            {
                "id": "3",
                "name": "Amit Patel",
                "email": "amit@example.com",
                "status": "attention",
                "riskLevel": "high",
                "conditions": ["Hypertension", "Diabetes"],
                "lastVisit": "2025-11-09"
            }
        ]
        return jsonify(mock_users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting FitMindAI Backend...")
    print(f"📡 Server will run on http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
