import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Apple, RefreshCw, Download, Loader2, AlertCircle, 
  ChefHat, Clock, Flame, CheckCircle, TrendingUp, Settings, Leaf
} from 'lucide-react';
import { supabase } from '../../supabaseClient';
import { useToast } from '@/hooks/use-toast';

const DietPlan = () => {
  const [step, setStep] = useState<'setup' | 'plan'>('setup');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [nutritionTargets, setNutritionTargets] = useState<any>(null);
  const [mealPlans, setMealPlans] = useState<any>(null);
  const { toast } = useToast();

  const [preferences, setPreferences] = useState({
    activity_level: 'moderate',
    goal: 'maintenance',
    max_prep_time: 45,
  });

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      const { data: profile } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (!profile) {
        throw new Error('Profile not found. Please complete onboarding first.');
      }

      const { data: conditions } = await supabase
        .from('user_conditions')
        .select('condition_name')
        .eq('user_id', user.id);

      const conditionsList = conditions?.map(c => c.condition_name) || [];

      let dietPref = 'Vegetarian';
      let goalFromProfile = 'maintenance';
      try {
        const parsed = typeof profile.dietary_preferences === 'string'
          ? JSON.parse(profile.dietary_preferences)
          : profile.dietary_preferences;
        dietPref = parsed?.type || 'Vegetarian';
        goalFromProfile = parsed?.goal?.toLowerCase().replace(' ', '_') || 'maintenance';
      } catch {}

      setUserProfile({
        age: profile.age,
        gender: profile.gender,
        weight_kg: profile.weight,
        height_cm: profile.height,
        medical_conditions: conditionsList,
        diet_type: dietPref,
      });

      setPreferences(prev => ({ ...prev, goal: goalFromProfile }));

    } catch (err: any) {
      setError(err.message);
      toast({
        title: 'Error',
        description: err.message,
        variant: 'destructive',
      });
    }
  };

  const handleGeneratePlan = async () => {
    if (!userProfile) return;

    setLoading(true);
    setError(null);

    try {
      const profileData = {
        ...userProfile,
        activity_level: preferences.activity_level,
        goal: preferences.goal,
        max_prep_time: preferences.max_prep_time,
      };

      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch('http://localhost:5000/api/diet/complete-meal-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate meal plan');
      }

      const data = await response.json();
      
      console.log('API Response:', data); // Debug log
      
      if (data.status === 'success') {
        setNutritionTargets(data.data.nutrition_targets);
        setMealPlans(data.data.meal_plans);
        setStep('plan');
        toast({
          title: 'Success!',
          description: 'Your personalized meal plan is ready',
        });
      } else {
        throw new Error('Invalid response format');
      }

    } catch (err: any) {
      console.error('Error generating plan:', err);
      setError(err.message);
      toast({
        title: 'Error',
        description: err.message || 'Failed to generate plan',
        variant: 'destructive',
      });
    }

    setLoading(false);
  };

  const handleSwapMeal = async (mealType: string) => {
    if (!userProfile || !nutritionTargets) return;
    
    setLoading(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const mealTargets = nutritionTargets.meal_breakdown[mealType];
      
      const response = await fetch('http://localhost:5000/api/diet/recommend-recipes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({
          meal: mealType,
          calories: mealTargets.calories,
          protein_g: mealTargets.protein_g,
          carbs_g: mealTargets.carbs_g,
          fat_g: mealTargets.fat_g,
          diet: userProfile.diet_type,
          medical_conditions: userProfile.medical_conditions,
          top_n: 3,
        }),
      });

      if (!response.ok) throw new Error('Failed to get alternative recipes');

      const data = await response.json();
      
      if (data.status === 'success' && data.data.recommendations.length > 0) {
        setMealPlans((prev: any) => ({
          ...prev,
          [mealType]: data.data.recommendations,
        }));
        
        toast({
          title: 'Meal Swapped',
          description: `New ${mealType} options loaded`,
        });
      }

    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to swap meal',
        variant: 'destructive',
      });
    }
    setLoading(false);
  };

  // ========== SETUP FORM ==========
  if (step === 'setup') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
              <Settings className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold mb-3 gradient-text">Customize Your Diet Plan</h1>
            <p className="text-lg text-muted-foreground">
              Tell us about your activity and goals for precise nutrition targets
            </p>
          </div>

          <div className="glass-card p-8 space-y-6">
            {/* Activity Level */}
            <div className="space-y-3">
              <Label className="text-lg font-semibold">Activity Level</Label>
              <RadioGroup 
                value={preferences.activity_level} 
                onValueChange={(val) => setPreferences({ ...preferences, activity_level: val })}
              >
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="sedentary" id="sedentary" />
                  <Label htmlFor="sedentary" className="cursor-pointer flex-1">
                    <p className="font-medium">Sedentary</p>
                    <p className="text-xs text-muted-foreground">Little to no exercise</p>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="lightly_active" id="lightly_active" />
                  <Label htmlFor="lightly_active" className="cursor-pointer flex-1">
                    <p className="font-medium">Lightly Active</p>
                    <p className="text-xs text-muted-foreground">Exercise 1-3 days/week</p>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="moderate" id="moderate" />
                  <Label htmlFor="moderate" className="cursor-pointer flex-1">
                    <p className="font-medium">Moderately Active</p>
                    <p className="text-xs text-muted-foreground">Exercise 3-5 days/week</p>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="very_active" id="very_active" />
                  <Label htmlFor="very_active" className="cursor-pointer flex-1">
                    <p className="font-medium">Very Active</p>
                    <p className="text-xs text-muted-foreground">Exercise 6-7 days/week</p>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="extra_active" id="extra_active" />
                  <Label htmlFor="extra_active" className="cursor-pointer flex-1">
                    <p className="font-medium">Extremely Active</p>
                    <p className="text-xs text-muted-foreground">Athlete / physical job</p>
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {/* Goal */}
            <div className="space-y-3">
              <Label className="text-lg font-semibold">Health Goal</Label>
              <RadioGroup 
                value={preferences.goal} 
                onValueChange={(val) => setPreferences({ ...preferences, goal: val })}
              >
                {['weight_loss', 'weight_gain', 'muscle_gain', 'maintenance', 'general_health'].map(goal => (
                  <div key={goal} className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                    <RadioGroupItem value={goal} id={goal} />
                    <Label htmlFor={goal} className="cursor-pointer capitalize">
                      {goal.replace('_', ' ')}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            {/* Max Prep Time */}
            <div className="space-y-3">
              <Label className="text-lg font-semibold">Maximum Cooking Time</Label>
              <Select 
                value={preferences.max_prep_time.toString()} 
                onValueChange={(val) => setPreferences({ ...preferences, max_prep_time: parseInt(val) })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="15">15 minutes</SelectItem>
                  <SelectItem value="30">30 minutes</SelectItem>
                  <SelectItem value="45">45 minutes</SelectItem>
                  <SelectItem value="60">1 hour</SelectItem>
                  <SelectItem value="90">1.5 hours</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button 
              onClick={handleGeneratePlan} 
              disabled={loading || !userProfile}
              className="w-full btn-glow"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Generating Your Plan...
                </>
              ) : (
                <>
                  <Apple className="mr-2 h-5 w-5" />
                  Generate My Diet Plan
                </>
              )}
            </Button>

            {error && (
              <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ========== PLAN VIEW ==========
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
            <Apple className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-3 gradient-text">Your AI Diet Plan</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Personalized meal recommendations based on your health profile
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setStep('setup')}
            className="mt-4"
          >
            <Settings className="mr-2 h-4 w-4" />
            Adjust Preferences
          </Button>
        </div>

        {/* Nutrition Targets - TIER 1 */}
        {nutritionTargets && (
          <div className="glass-card p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Daily Nutrition Targets</h2>
              <Badge variant="outline" className="text-xs">TIER 1: Personalized Calculation</Badge>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-xl bg-gradient-to-br from-warm/20 to-warm/10">
                <Flame className="h-6 w-6 mx-auto mb-2 text-warm" />
                <p className="text-xs text-muted-foreground mb-1">Target Calories</p>
                <p className="text-2xl font-bold">{Math.round(nutritionTargets.target_calories)}</p>
                <p className="text-xs text-muted-foreground mt-1">TDEE: {Math.round(nutritionTargets.tdee)}</p>
              </div>
              <div className="text-center p-4 rounded-xl bg-gradient-to-br from-primary/20 to-primary/10">
                <p className="text-xs text-muted-foreground mb-1">Protein</p>
                <p className="text-2xl font-bold text-primary">{Math.round(nutritionTargets.daily_macros.protein_g)}g</p>
              </div>
              <div className="text-center p-4 rounded-xl bg-gradient-to-br from-accent/20 to-accent/10">
                <p className="text-xs text-muted-foreground mb-1">Carbs</p>
                <p className="text-2xl font-bold text-accent">{Math.round(nutritionTargets.daily_macros.carbs_g)}g</p>
              </div>
              <div className="text-center p-4 rounded-xl bg-gradient-to-br from-secondary/20 to-secondary/10">
                <p className="text-xs text-muted-foreground mb-1">Fat</p>
                <p className="text-2xl font-bold text-secondary">{Math.round(nutritionTargets.daily_macros.fat_g)}g</p>
              </div>
            </div>
          </div>
        )}

        {/* Medical Alert */}
        {userProfile?.medical_conditions?.length > 0 && (
          <div className="glass-card p-4 mb-6 bg-blue-50/50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-blue-900 dark:text-blue-100">Medical-Aware Filtering Active</p>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  All meals filtered for: {userProfile.medical_conditions.join(', ')}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Meals Grid - TIER 2 */}
        {mealPlans && Object.keys(mealPlans).length > 0 ? (
          <>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Today's Meal Plan</h2>
              <Badge variant="outline" className="text-xs">TIER 2: Content-Based Recommendations</Badge>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {Object.entries(mealPlans).map(([mealType, recipes]: [string, any]) => {
                const recipe = Array.isArray(recipes) && recipes.length > 0 ? recipes[0] : null;
                
                if (!recipe) {
                  return (
                    <div key={mealType} className="glass-card-elevated p-6">
                      <p className="text-muted-foreground text-center">No recommendations for {mealType}</p>
                    </div>
                  );
                }

                return (
                  <div key={mealType} className="glass-card-elevated p-6 hover:scale-[1.02] transition-all">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <ChefHat className="h-5 w-5 text-primary" />
                          <span className="text-sm font-medium text-muted-foreground uppercase">{mealType}</span>
                          <Badge variant="outline" className="text-xs">{recipe.cuisine || 'Indian'}</Badge>
                        </div>
                        <h3 className="text-xl font-bold mb-1">{recipe.recipe_name}</h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="h-4 w-4" />
                          <span>{recipe.time_mins} mins</span>
                          <Badge variant="secondary" className="text-xs ml-2">{recipe.diet}</Badge>
                        </div>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleSwapMeal(mealType)}
                        disabled={loading}
                        title="Get different recipe"
                      >
                        <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                      </Button>
                    </div>

                    {/* Nutrition Info */}
                    <div className="grid grid-cols-4 gap-2 mb-4 p-4 rounded-xl bg-muted/50">
                      <div className="text-center">
                        <Flame className="h-4 w-4 mx-auto mb-1 text-warm" />
                        <p className="text-xs text-muted-foreground">Calories</p>
                        <p className="font-bold">{Math.round(recipe.nutrition?.calories || 0)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground mb-1">Protein</p>
                        <p className="font-bold text-primary">{Math.round(recipe.nutrition?.protein_g || 0)}g</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground mb-1">Carbs</p>
                        <p className="font-bold text-accent">{Math.round(recipe.nutrition?.carbs_g || 0)}g</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground mb-1">Fat</p>
                        <p className="font-bold text-secondary">{Math.round(recipe.nutrition?.fat_g || 0)}g</p>
                      </div>
                    </div>

                    {/* Match Score */}
                    <div className="mb-4 p-3 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-green-600" />
                          <span className="text-sm font-medium text-green-900 dark:text-green-100">
                            Nutrition Match: {Math.round(recipe.match_score || 0)}%
                          </span>
                        </div>
                        {recipe.nutrition?.sodium_mg > 600 && userProfile?.medical_conditions?.includes('Hypertension') && (
                          <Badge variant="destructive" className="text-xs">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            High Sodium
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Protein Suggestion */}
                    {recipe.protein_suggestion && (
                      <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 mb-4">
                        <p className="text-sm text-blue-900 dark:text-blue-100">
                          <strong>💡 Protein Tip:</strong> {recipe.protein_suggestion}
                        </p>
                      </div>
                    )}

                    {/* More Options */}
                    {Array.isArray(recipes) && recipes.length > 1 && (
                      <div className="pt-4 border-t">
                        <p className="text-sm text-muted-foreground mb-2">
                          {recipes.length - 1} more option{recipes.length > 2 ? 's' : ''} available
                        </p>
                        <div className="flex gap-2 flex-wrap">
                          {recipes.slice(1, 3).map((alt: any, idx: number) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {alt.recipe_name?.slice(0, 25)}...
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="glass-card p-8 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-semibold mb-2">No Meal Recommendations Available</p>
            <p className="text-muted-foreground">Try adjusting your preferences or regenerating the plan</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-3 justify-center">
          <Button variant="outline" onClick={() => setStep('setup')} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Regenerate Plan
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Download PDF
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DietPlan;
