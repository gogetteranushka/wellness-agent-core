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

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for React frontend
load_dotenv()

diet_engine = DietEngine()

# Auth Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Load datasets
foods = pd.read_csv('data/Food_and_Nutrition.csv')
foods.columns = foods.columns.str.lower().str.strip()

# Load nutrition model at startup
try:
    nutrition_model = joblib.load('models/indb_nutrition_predictor_best.pkl')
    print("✅ Nutrition model loaded")
except Exception as e:
    print(f"❌ Error loading nutrition model: {e}")
    nutrition_model = None

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
# ✅ ADD THIS: Health Check Endpoint
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check to verify backend is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'FitMindAI Backend is running',
        'services': {
            'symptom_classifier': symptom_classifier is not None,
            'nutrition_model': nutrition_model is not None,
            'recipe_recommender': recipe_recommender is not None
        }
    }), 200


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
        # Convert underscores to spaces for display
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
        
        # Convert symptoms back to model format (lowercase with underscores)
        symptoms_formatted = [s.lower().replace(' ', '_') for s in symptoms]
        
        print(f"📋 User selected: {symptoms}")
        print(f"📋 Formatted for model: {symptoms_formatted}")
        
        # Create symptom vector
        symptom_vector = np.zeros(len(symptom_list))
        for i, symptom in enumerate(symptom_list):
            if symptom.lower() in symptoms_formatted:
                symptom_vector[i] = 1
                print(f"✅ Matched: {symptom}")
        
        print(f"📊 Symptom vector sum: {symptom_vector.sum()}")
        
        # ✅ FIX: Feature names must exactly match training!
        features = dict(zip(symptom_list, symptom_vector))
        features['symptom_count'] = int(symptom_vector.sum())
        symptom_df = pd.DataFrame([features])  # columns: all symptom features + symptom_count
        
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
        
        # Validate required fields
        required = ['age', 'gender', 'weight_kg', 'height_cm', 'activity_level', 'goal']
        for field in required:
            if field not in user_profile:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Generate plan
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
        
        # Extract targets
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
        
        # Get recommendations
        recommendations_df = recipe_recommender.recommend(
            targets,
            medical_conditions=medical_conditions,
            top_n=top_n
        )
        
        # Convert to JSON-friendly format
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
        
        # Step 1: Calculate nutrition targets (TIER 1)
        nutrition_plan = diet_engine.generate_personalized_plan(user_profile)
        
        # Step 2: Get recommendations for each meal (TIER 2)
        meals = ['breakfast', 'lunch', 'dinner', 'snacks']
        meal_plans = {}
        
        for meal in meals:
            meal_targets = {
                'course': meal.capitalize(),
                'calories': nutrition_plan['meal_breakdown'][meal]['calories'],
                'protein_g': nutrition_plan['meal_breakdown'][meal]['protein_g'],
                'carbs_g': nutrition_plan['meal_breakdown'][meal]['carbs_g'],
                'fat_g': nutrition_plan['meal_breakdown'][meal]['fat_g'],
                'diet': user_profile.get('diet_type', 'Vegetarian'),
                'max_time_mins': user_profile.get('max_prep_time', 45)
            }

            # Special handling for snacks
            if meal == 'snacks':
                meal_targets['calories'] = meal_targets['calories'] * 2
                meal_targets['course'] = 'Snack|Appetizer|Side Dish'
            
            recommendations_df = recipe_recommender.recommend(
                meal_targets,
                medical_conditions=user_profile.get('medical_conditions', []),
                top_n=3
            )
            
            # Convert to JSON
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
                "meal_plans": meal_plans
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
        # Check if hybrid recommender is available
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
# NUTRITION PREDICTOR (INDB Model)
# ============================================================================
@app.route('/api/predict-nutrition', methods=['POST'])
def predict_nutrition():
    """Predict recipe nutrition from ingredients"""
    try:
        if not nutrition_model:
            return jsonify({'error': 'Nutrition model not loaded'}), 500
        
        data = request.json
        
        # If features are pre-calculated
        if 'features' in data:
            features_dict = data['features']
        # If raw ingredients provided
        elif 'ingredients' in data:
            features_dict = extract_features_from_ingredients(data['ingredients'])
        else:
            return jsonify({'error': 'Must provide either "ingredients" or "features"'}), 400
        
        # Feature order (must match training)
        feature_order = [
            'ingredient_count', 'total_weight_grams', 'has_milk', 'has_sugar',
            'has_rice', 'has_dal', 'has_paneer', 'has_ghee', 'has_butter',
            'has_cream', 'has_oil', 'has_onion', 'has_tomato', 'has_potato',
            'has_chicken', 'has_vegetables', 'dairy_grams', 'grain_grams',
            'protein_source_grams', 'fat_source_grams', 'vegetable_grams',
            'spice_grams', 'rich_ingredient_count'
        ]
        
        features = [features_dict.get(f, 0) for f in feature_order]
        features_array = np.array(features).reshape(1, -1)
        
        predicted_calories = nutrition_model.predict(features_array)[0]
        
        mae = 45
        
        response = {
            'predicted_nutrition': {
                'calories': round(predicted_calories, 1),
                'confidence_range': {
                    'min': round(predicted_calories - mae, 1),
                    'max': round(predicted_calories + mae, 1)
                }
            },
            'model_info': {
                'algorithm': 'Gradient Boosting',
                'accuracy': '±45 kcal',
                'r_squared': 0.871
            },
            'features_used': features_dict
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Nutrition prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def extract_features_from_ingredients(ingredients_list):
    """Convert raw ingredient list to features"""
    features = {
        'ingredient_count': len(ingredients_list),
        'total_weight_grams': 0,
        'has_milk': 0, 'has_sugar': 0, 'has_rice': 0, 'has_dal': 0,
        'has_paneer': 0, 'has_ghee': 0, 'has_butter': 0, 'has_cream': 0,
        'has_oil': 0, 'has_onion': 0, 'has_tomato': 0, 'has_potato': 0,
        'has_chicken': 0, 'has_vegetables': 0,
        'dairy_grams': 0, 'grain_grams': 0, 'protein_source_grams': 0,
        'fat_source_grams': 0, 'vegetable_grams': 0, 'spice_grams': 0,
        'rich_ingredient_count': 0
    }
    
    def convert_to_grams(amount, unit):
        conversions = {
            'tsp': 5, 'tbsp': 15, 'cup': 240, 'ml': 1, 'g': 1, 'kg': 1000
        }
        unit_clean = unit.lower().strip()
        return amount * conversions.get(unit_clean, 1)
    
    for ing in ingredients_list:
        name_lower = ing['name'].lower()
        amount_grams = convert_to_grams(ing['amount'], ing['unit'])
        
        features['total_weight_grams'] += amount_grams
        
        # Binary flags
        if 'milk' in name_lower: features['has_milk'] = 1
        if 'sugar' in name_lower: features['has_sugar'] = 1
        if 'rice' in name_lower: features['has_rice'] = 1
        if 'dal' in name_lower or 'lentil' in name_lower: features['has_dal'] = 1
        if 'paneer' in name_lower: features['has_paneer'] = 1
        if 'ghee' in name_lower: features['has_ghee'] = 1
        if 'butter' in name_lower: features['has_butter'] = 1
        if 'cream' in name_lower: features['has_cream'] = 1
        if 'oil' in name_lower: features['has_oil'] = 1
        if 'onion' in name_lower: features['has_onion'] = 1
        if 'tomato' in name_lower: features['has_tomato'] = 1
        if 'potato' in name_lower: features['has_potato'] = 1
        if 'chicken' in name_lower: features['has_chicken'] = 1
        if any(veg in name_lower for veg in ['vegetable', 'carrot', 'peas', 'beans']):
            features['has_vegetables'] = 1
        
        # Category totals
        if any(dairy in name_lower for dairy in ['milk', 'cream', 'paneer', 'butter', 'ghee']):
            features['dairy_grams'] += amount_grams
        if any(grain in name_lower for grain in ['rice', 'wheat', 'flour', 'bread']):
            features['grain_grams'] += amount_grams
        if any(protein in name_lower for protein in ['dal', 'lentil', 'chicken', 'paneer']):
            features['protein_source_grams'] += amount_grams
        if any(fat in name_lower for fat in ['oil', 'ghee', 'butter']):
            features['fat_source_grams'] += amount_grams
        if any(veg in name_lower for veg in ['vegetable', 'onion', 'tomato', 'carrot']):
            features['vegetable_grams'] += amount_grams
        if any(spice in name_lower for spice in ['spice', 'masala', 'salt', 'pepper']):
            features['spice_grams'] += amount_grams
    
    features['rich_ingredient_count'] = sum([
        features['has_cream'], features['has_butter'],
        features['has_ghee'], features['has_paneer']
    ])
    
    return features
# ============================================================================
# USER MANAGEMENT (For Dashboard)
# ============================================================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users for dashboard - Mock data for now"""
    try:
        # TODO: Replace with actual Supabase query later
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
