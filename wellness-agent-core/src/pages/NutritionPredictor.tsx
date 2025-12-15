// File: src/pages/NutritionPredictor.tsx

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Plus, Trash2, Calculator, Loader2, ChefHat, Sparkles, TrendingUp } from 'lucide-react';
import { supabase } from '../../supabaseClient';

interface Ingredient {
  id: string;
  name: string;
  amount: string;
  unit: string;
}

interface PredictionResult {
  predicted_nutrition: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    confidence_range: {
      min: number;
      max: number;
    };
  };
  model_info: {
    algorithm: string;
    accuracy: string;
    r_squared: number;
  };
}

const NutritionPredictor = () => {
  const [ingredients, setIngredients] = useState<Ingredient[]>([
    { id: '1', name: '', amount: '', unit: 'g' }
  ]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [recipeName, setRecipeName] = useState('');

  const units = ['g', 'ml', 'tsp', 'tbsp', 'cup', 'kg'];

  const addIngredient = () => {
    setIngredients([
      ...ingredients,
      { id: Date.now().toString(), name: '', amount: '', unit: 'g' }
    ]);
  };

  const removeIngredient = (id: string) => {
    if (ingredients.length > 1) {
      setIngredients(ingredients.filter(ing => ing.id !== id));
    }
  };

  const updateIngredient = (id: string, field: keyof Ingredient, value: string) => {
    setIngredients(
      ingredients.map(ing =>
        ing.id === id ? { ...ing, [field]: value } : ing
      )
    );
  };

  const predictNutrition = async () => {
    const validIngredients = ingredients.filter(
      ing => ing.name.trim() && ing.amount.trim()
    );

    if (validIngredients.length === 0) {
      alert('Please add at least one ingredient with name and amount');
      return;
    }

    setLoading(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const payload = {
        ingredients: validIngredients.map(ing => ({
          name: ing.name,
          amount: parseFloat(ing.amount),
          unit: ing.unit
        }))
      };

      const response = await fetch('http://localhost:5000/api/predict-nutrition', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Prediction failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to predict nutrition. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setIngredients([{ id: '1', name: '', amount: '', unit: 'g' }]);
    setResult(null);
    setRecipeName('');
  };

  const loadTemplate = (template: string) => {
    const templates: { [key: string]: Ingredient[] } = {
      dalMakhani: [
        { id: '1', name: 'urad dal', amount: '200', unit: 'g' },
        { id: '2', name: 'butter', amount: '30', unit: 'g' },
        { id: '3', name: 'cream', amount: '50', unit: 'ml' },
        { id: '4', name: 'tomato', amount: '100', unit: 'g' },
        { id: '5', name: 'onion', amount: '50', unit: 'g' },
        { id: '6', name: 'spices', amount: '10', unit: 'g' }
      ],
      paneerTikka: [
        { id: '1', name: 'paneer', amount: '200', unit: 'g' },
        { id: '2', name: 'yogurt', amount: '100', unit: 'g' },
        { id: '3', name: 'oil', amount: '20', unit: 'ml' },
        { id: '4', name: 'onion', amount: '50', unit: 'g' },
        { id: '5', name: 'bell pepper', amount: '50', unit: 'g' },
        { id: '6', name: 'spices', amount: '10', unit: 'g' }
      ],
      simpleDalRice: [
        { id: '1', name: 'rice', amount: '150', unit: 'g' },
        { id: '2', name: 'dal', amount: '50', unit: 'g' },
        { id: '3', name: 'ghee', amount: '10', unit: 'g' }
      ]
    };

    setIngredients(templates[template] || []);
    setResult(null);
    setRecipeName('');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
            <ChefHat className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">Recipe Nutrition Predictor</h1>
          <p className="text-lg text-muted-foreground">
            AI-powered nutrition prediction • Gradient Boosting • ±45 cal accuracy
          </p>
        </div>

        {/* Quick Templates */}
        <div className="glass-card p-6 mb-6 animate-slide-up">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-5 w-5 text-accent" />
            <h3 className="font-semibold">Quick Templates</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadTemplate('dalMakhani')}
            >
              Dal Makhani
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadTemplate('paneerTikka')}
            >
              Paneer Tikka
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadTemplate('simpleDalRice')}
            >
              Dal Rice
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="glass-card-elevated p-6 animate-fade-in">
            <h2 className="text-xl font-semibold mb-4">Recipe Ingredients</h2>

            {/* Recipe Name */}
            <div className="mb-4">
              <label className="text-sm font-medium mb-2 block text-muted-foreground">
                Recipe Name (Optional)
              </label>
              <Input
                placeholder="e.g., Grandma's Dal Makhani"
                value={recipeName}
                onChange={(e) => setRecipeName(e.target.value)}
                className="glass-input"
              />
            </div>

            {/* Ingredients List */}
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2 mb-4">
              {ingredients.map((ing) => (
                <div key={ing.id} className="flex gap-2 items-start">
                  <div className="flex-1">
                    <Input
                      placeholder="Ingredient name"
                      value={ing.name}
                      onChange={(e) => updateIngredient(ing.id, 'name', e.target.value)}
                      className="glass-input"
                    />
                  </div>
                  <div className="w-24">
                    <Input
                      type="number"
                      placeholder="Amount"
                      value={ing.amount}
                      onChange={(e) => updateIngredient(ing.id, 'amount', e.target.value)}
                      className="glass-input"
                    />
                  </div>
                  <div className="w-20">
                    <select
                      className="w-full px-3 py-2 border rounded-md bg-background"
                      value={ing.unit}
                      onChange={(e) => updateIngredient(ing.id, 'unit', e.target.value)}
                    >
                      {units.map(unit => (
                        <option key={unit} value={unit}>{unit}</option>
                      ))}
                    </select>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeIngredient(ing.id)}
                    disabled={ingredients.length === 1}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>

            <Button
              variant="outline"
              onClick={addIngredient}
              className="w-full mb-4"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Ingredient
            </Button>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button
                onClick={predictNutrition}
                disabled={loading}
                className="flex-1"
                variant="hero"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Predicting...
                  </>
                ) : (
                  <>
                    <Calculator className="mr-2 h-4 w-4" />
                    Predict Nutrition
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={clearForm}>
                Clear
              </Button>
            </div>
          </div>

          {/* Results Section */}
          <div className="glass-card-elevated p-6 animate-fade-in">
            <h2 className="text-xl font-semibold mb-4">Prediction Results</h2>

            {!result ? (
              <div className="text-center py-12 text-muted-foreground">
                <Calculator className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Add ingredients and click "Predict" to see nutrition</p>
              </div>
            ) : (
              <div className="space-y-6">
                {recipeName && (
                  <div>
                    <h3 className="text-2xl font-bold gradient-text">{recipeName}</h3>
                  </div>
                )}

                {/* Calories Card */}
                <div className="glass-card p-6 bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground mb-2 flex items-center justify-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Predicted Calories
                    </p>
                    <p className="text-5xl font-bold gradient-text mb-2">
                      {result.predicted_nutrition.calories}
                    </p>
                    <p className="text-xs text-muted-foreground">kcal per serving</p>
                    
                    <div className="mt-4 pt-4 border-t border-border">
                      <p className="text-sm font-medium mb-1">Confidence Range</p>
                      <p className="text-lg font-semibold">
                        {result.predicted_nutrition.confidence_range.min} - {' '}
                        {result.predicted_nutrition.confidence_range.max} kcal
                      </p>
                    </div>
                  </div>
                </div>

                {/* Macros Breakdown */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="glass-card p-4 text-center">
                    <p className="text-sm text-muted-foreground mb-1">Protein</p>
                    <p className="text-2xl font-bold text-primary">
                      {result.predicted_nutrition.protein_g}g
                    </p>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <p className="text-sm text-muted-foreground mb-1">Carbs</p>
                    <p className="text-2xl font-bold text-accent">
                      {result.predicted_nutrition.carbs_g}g
                    </p>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <p className="text-sm text-muted-foreground mb-1">Fats</p>
                    <p className="text-2xl font-bold text-orange-500">
                      {result.predicted_nutrition.fat_g}g
                    </p>
                  </div>
                </div>

                {/* Model Info */}
                <div className="space-y-3">
                  <h4 className="font-semibold">Model Information</h4>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Algorithm:</span>
                    <Badge variant="secondary">{result.model_info.algorithm}</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Accuracy:</span>
                    <Badge variant="outline">{result.model_info.accuracy}</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">R² Score:</span>
                    <Badge variant="outline">
                      {(result.model_info.r_squared * 100).toFixed(1)}%
                    </Badge>
                  </div>
                </div>

                {/* Disclaimer */}
                <div className="bg-muted/50 border border-border rounded-lg p-4">
                  <p className="text-xs text-muted-foreground">
                    <strong>Note:</strong> Predictions are based on Indian recipes using Gradient Boosting. 
                    Actual values may vary based on cooking method and ingredient quality.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NutritionPredictor;
