from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# Load datasets
symptom_desc = pd.read_csv('data/symptom_Description.csv')
symptom_precaution = pd.read_csv('data/symptom_precaution.csv')
symptom_severity = pd.read_csv('data/Symptom-severity.csv')
foods = pd.read_csv('data/Food_and_Nutrition.csv')

# Clean column names
for df in [symptom_desc, symptom_precaution, symptom_severity, foods]:
    df.columns = df.columns.str.lower().str.strip()

# Condition-to-nutrient mapping
CONDITION_NUTRIENT_MAP = {
    "Diabetes": {"increase": ["fiber", "protein"], "decrease": ["sugar", "carbohydrates"]},
    "Hypertension": {"increase": ["potassium", "fiber"], "decrease": ["sodium"]},
    "Obesity": {"increase": ["fiber"], "decrease": ["fat", "sugar"]},
    "Heart Disease": {"increase": ["fiber"], "decrease": ["fat"]}
}

# Helper function: Infer risk condition
def infer_risk_condition(bmi, cholesterol, chronic_disease=None):
    if chronic_disease and chronic_disease in CONDITION_NUTRIENT_MAP:
        return chronic_disease
    elif bmi > 30:
        return 'Obesity'
    elif cholesterol > 200:
        return 'Heart Disease'
    else:
        return 'Healthy'

# Helper function: Get meal recommendations
def get_meal_recommendations(risk_condition, dietary_preference=None):
    if risk_condition not in CONDITION_NUTRIENT_MAP:
        # Return random meal if healthy
        sample = foods.sample(1).iloc[0]
    else:
        # Filter by dietary preference if provided
        filtered = foods.copy()
        if dietary_preference:
            filtered = filtered[filtered['dietary preference'].str.lower() == dietary_preference.lower()]
        
        # Get best match (simplified for now)
        sample = filtered.sample(1).iloc[0] if len(filtered) > 0 else foods.sample(1).iloc[0]
    
    return {
        'breakfast': sample.get('breakfast suggestion', 'Oatmeal'),
        'lunch': sample.get('lunch suggestion', 'Grilled chicken salad'),
        'dinner': sample.get('dinner suggestion', 'Salmon with vegetables'),
        'snack': sample.get('snack suggestion', 'Greek yogurt'),
        'calories': int(sample.get('calories', 2000)),
        'protein': int(sample.get('protein', 100)),
        'carbohydrates': int(sample.get('carbohydrates', 250)),
        'fat': int(sample.get('fat', 60))
    }

# ========== API ENDPOINTS ==========

@app.route('/')
def home():
    return jsonify({"message": "Agentic AI for Wellness API", "status": "running"})

@app.route('/api/symptom-check', methods=['POST'])
def symptom_check():
    data = request.json
    symptoms = data.get('symptoms', [])
    
    # Mock prediction logic (will be replaced with ML model)
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    
    # Calculate severity
    total_severity = 0
    for symptom in symptoms:
        symptom_clean = symptom.lower().replace(' ', '')
        match = symptom_severity[symptom_severity['symptom'].str.replace(' ', '') == symptom_clean]
        if not match.empty:
            total_severity += match.iloc[0]['weight']
    
    # Mock condition prediction
    predicted_conditions = [
        {"condition": "Diabetes", "probability": 0.65, "severity": "Medium"},
        {"condition": "Hypertension", "probability": 0.45, "severity": "Low"}
    ]
    
    # Get precautions
    precautions = symptom_precaution.sample(3).to_dict('records') if len(symptom_precaution) > 0 else []
    
    return jsonify({
        "symptoms": symptoms,
        "total_severity": int(total_severity),
        "predicted_conditions": predicted_conditions,
        "precautions": precautions
    })

@app.route('/api/diet-plan', methods=['POST'])
def diet_plan():
    data = request.json
    bmi = data.get('bmi', 25)
    cholesterol = data.get('cholesterol', 180)
    chronic_disease = data.get('chronic_disease', None)
    dietary_preference = data.get('dietary_preference', None)
    
    # Infer risk
    risk = infer_risk_condition(bmi, cholesterol, chronic_disease)
    
    # Get meal recommendations
    meals = get_meal_recommendations(risk, dietary_preference)
    
    return jsonify({
        "risk_condition": risk,
        "meal_plan": meals,
        "nutrient_advice": CONDITION_NUTRIENT_MAP.get(risk, {})
    })

@app.route('/api/analytics', methods=['POST'])
def analytics():
    data = request.json
    
    # Mock analytics data
    return jsonify({
        "daily_calories": [1800, 2000, 1950, 2100, 1850],
        "daily_protein": [90, 100, 95, 105, 88],
        "nutrient_gaps": {
            "fiber": {"current": 20, "target": 30, "unit": "g"},
            "sodium": {"current": 2400, "target": 1500, "unit": "mg"}
        },
        "bmi_trend": [28.5, 28.2, 27.9, 27.6, 27.4]
    })

@app.route('/api/explorer/conditions', methods=['GET'])
def get_conditions():
    return jsonify({
        "conditions": list(CONDITION_NUTRIENT_MAP.keys())
    })

@app.route('/api/explorer/condition/<condition>', methods=['GET'])
def get_condition_details(condition):
    if condition not in CONDITION_NUTRIENT_MAP:
        return jsonify({"error": "Condition not found"}), 404
    
    return jsonify({
        "condition": condition,
        "nutrient_recommendations": CONDITION_NUTRIENT_MAP[condition]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
