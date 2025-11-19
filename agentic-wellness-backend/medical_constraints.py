# File: backend/medical_constraints.py

MEDICAL_CONSTRAINTS = {
    'diabetes': {
        'max_carbs_per_serving': 45,  # grams
        'max_sugar_per_serving': 15,   # grams
        'avoid_ingredients': ['white rice', 'white bread', 'sugar', 'honey', 'jaggery'],
        'preferred_ingredients': ['whole grain', 'quinoa', 'brown rice', 'oats', 'barley']
    },
    
    'pre_diabetes': {
        'max_carbs_per_serving': 50,
        'avoid_ingredients': ['white rice', 'sugar', 'refined flour'],
        'preferred_ingredients': ['whole grain', 'oats', 'vegetables']
    },
    
    'hypertension': {
        'max_sodium_per_serving': 600,  # mg (AHA recommendation: <2300mg/day)
        'avoid_ingredients': ['salt', 'soy sauce', 'pickles', 'processed meat', 'papad'],
        'preferred_ingredients': ['low sodium', 'fresh herbs', 'lemon', 'garlic']
    },
    
    'heart_disease': {
        'max_saturated_fat_per_serving': 7,  # grams
        'max_cholesterol_per_serving': 200,  # mg
        'max_sodium_per_serving': 600,
        'avoid_ingredients': ['butter', 'ghee', 'cream', 'full-fat cheese', 'red meat', 'coconut oil'],
        'preferred_ingredients': ['olive oil', 'fish', 'lean chicken', 'nuts', 'avocado', 'oats']
    },
    
    'high_cholesterol': {
        'max_cholesterol_per_serving': 200,
        'max_saturated_fat_per_serving': 7,
        'avoid_ingredients': ['egg yolk', 'shrimp', 'butter', 'full-fat dairy', 'organ meat'],
        'preferred_ingredients': ['oats', 'barley', 'beans', 'apples', 'fish', 'almonds']
    },
    
    'kidney_disease': {
        'max_protein_per_serving': 20,  # grams
        'max_sodium_per_serving': 500,  # mg
        'max_potassium_per_serving': 200,  # mg
        'avoid_ingredients': ['beans', 'lentils', 'nuts', 'cheese', 'tomatoes', 'bananas', 'potatoes'],
        'preferred_ingredients': ['rice', 'cabbage', 'cucumber', 'apple', 'white bread']
    },
    
    'celiac_disease': {
        'required_diet': 'Gluten Free',
        'avoid_ingredients': ['wheat', 'barley', 'rye', 'oats', 'bread', 'pasta', 'atta', 'maida']
    },
    
    'lactose_intolerance': {
        'avoid_ingredients': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'paneer', 'ghee', 'curd']
    }
}
