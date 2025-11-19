import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Heart, ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '../../supabaseClient';

const Onboarding = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  // Form state
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    height: '',
    weight: '',
    medical_conditions: [] as string[],
    dietary_preferences: '',
    goal: '',
  });

  const medicalConditions = [
    'Diabetes',
    'Hypertension',
    'Kidney Disease',
    'Heart Disease',
    'PCOS',
    'Thyroid Disorder',
    'None',
  ];

  const dietaryPreferences = [
    'Vegetarian',
    'Vegan',
    'Non-Vegetarian',
    'Eggetarian',
    'No Preference',
  ];

  const goals = [
    'Weight Loss',
    'Weight Gain',
    'Muscle Gain',
    'Maintenance',
    'General Health',
  ];

  const handleConditionToggle = (condition: string) => {
    if (condition === 'None') {
      setFormData({ ...formData, medical_conditions: ['None'] });
    } else {
      const filtered = formData.medical_conditions.filter(c => c !== 'None');
      if (filtered.includes(condition)) {
        setFormData({
          ...formData,
          medical_conditions: filtered.filter(c => c !== condition),
        });
      } else {
        setFormData({
          ...formData,
          medical_conditions: [...filtered, condition],
        });
      }
    }
  };

  const handleSubmit = async () => {
    setLoading(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      // 1. Insert into user_profiles (only columns that exist!)
      const { error: profileError } = await supabase
        .from('user_profiles')
        .insert({
          user_id: user.id,
          age: formData.age ? parseInt(formData.age) : null,
          gender: formData.gender,
          height: formData.height ? parseFloat(formData.height) : null,
          weight: formData.weight ? parseFloat(formData.weight) : null,
          dietary_preferences: JSON.stringify({
            type: formData.dietary_preferences,
            goal: formData.goal
          }),
        });

      if (profileError) throw profileError;

      // 2. Insert medical conditions into user_conditions
      if (formData.medical_conditions.length > 0 && !formData.medical_conditions.includes('None')) {
        const conditionsData = formData.medical_conditions.map(condition => ({
          user_id: user.id,
          condition_name: condition,
          diagnosed_date: new Date().toISOString().split('T')[0],
        }));

        const { error: conditionsError } = await supabase
          .from('user_conditions')
          .insert(conditionsData);

        if (conditionsError) throw conditionsError;
      }

      toast({
        title: 'Profile Complete!',
        description: 'Your health profile has been created successfully.',
      });

      navigate('/profile');
    } catch (error: any) {
      console.error('Onboarding error:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to save profile',
        variant: 'destructive',
      });
    }

    setLoading(false);
  };

  const nextStep = () => {
    // Validation for each step
    if (step === 1) {
      if (!formData.age || !formData.gender || !formData.height || !formData.weight) {
        toast({
          title: 'Missing Information',
          description: 'Please fill in all basic information fields.',
          variant: 'destructive',
        });
        return;
      }
    }
    if (step === 2 && formData.medical_conditions.length === 0) {
      toast({
        title: 'Select Conditions',
        description: 'Please select your medical conditions or "None".',
        variant: 'destructive',
      });
      return;
    }
    if (step === 3 && !formData.dietary_preferences) {
      toast({
        title: 'Select Diet',
        description: 'Please select your dietary preference.',
        variant: 'destructive',
      });
      return;
    }

    if (step < 4) setStep(step + 1);
  };

  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/20 via-background to-accent/20 p-4">
      <div className="glass-card w-full max-w-2xl p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Heart className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold gradient-text">Complete Your Profile</h1>
          <p className="text-muted-foreground">
            Help us personalize your health journey (Step {step} of 4)
          </p>
        </div>
        {/* Progress Bar */}
        <div className="flex gap-2">
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              className={`h-2 flex-1 rounded-full transition-all ${
                s <= step ? 'bg-gradient-to-r from-primary to-accent' : 'bg-muted'
              }`}
            />
          ))}
        </div>

        {/* Step 1: Basic Info */}
        {step === 1 && (
          <div className="space-y-4 animate-fade-in">
            <h2 className="text-xl font-semibold">Basic Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age">Age *</Label>
                <Input
                  id="age"
                  type="number"
                  placeholder="25"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  className="glass-card-elevated"
                />
              </div>
              <div className="space-y-2">
                <Label>Gender *</Label>
                <RadioGroup value={formData.gender} onValueChange={(val) => setFormData({ ...formData, gender: val })}>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="male" id="male" />
                    <Label htmlFor="male">Male</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="female" id="female" />
                    <Label htmlFor="female">Female</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="other" id="other" />
                    <Label htmlFor="other">Other</Label>
                  </div>
                </RadioGroup>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="height">Height (cm) *</Label>
                <Input
                  id="height"
                  type="number"
                  placeholder="170"
                  value={formData.height}
                  onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                  className="glass-card-elevated"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="weight">Weight (kg) *</Label>
                <Input
                  id="weight"
                  type="number"
                  placeholder="65"
                  value={formData.weight}
                  onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                  className="glass-card-elevated"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Medical Conditions */}
        {step === 2 && (
          <div className="space-y-4 animate-fade-in">
            <h2 className="text-xl font-semibold">Medical Conditions</h2>
            <p className="text-sm text-muted-foreground">Select all that apply</p>
            <div className="grid grid-cols-2 gap-3">
              {medicalConditions.map((condition) => (
                <div key={condition} className="flex items-center space-x-2 glass-card-elevated p-3 rounded-lg">
                  <Checkbox
                    id={condition}
                    checked={formData.medical_conditions.includes(condition)}
                    onCheckedChange={() => handleConditionToggle(condition)}
                  />
                  <Label htmlFor={condition} className="cursor-pointer">
                    {condition}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Dietary Preferences */}
        {step === 3 && (
          <div className="space-y-4 animate-fade-in">
            <h2 className="text-xl font-semibold">Dietary Preferences</h2>
            <RadioGroup
              value={formData.dietary_preferences}
              onValueChange={(val) => setFormData({ ...formData, dietary_preferences: val })}
            >
              {dietaryPreferences.map((pref) => (
                <div key={pref} className="flex items-center space-x-2 glass-card-elevated p-3 rounded-lg">
                  <RadioGroupItem value={pref} id={pref} />
                  <Label htmlFor={pref} className="cursor-pointer flex-1">
                    {pref}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
        )}

        {/* Step 4: Goals */}
        {step === 4 && (
          <div className="space-y-4 animate-fade-in">
            <h2 className="text-xl font-semibold">Your Health Goals</h2>
            <RadioGroup value={formData.goal} onValueChange={(val) => setFormData({ ...formData, goal: val })}>
              {goals.map((goal) => (
                <div key={goal} className="flex items-center space-x-2 glass-card-elevated p-3 rounded-lg">
                  <RadioGroupItem value={goal} id={goal} />
                  <Label htmlFor={goal} className="cursor-pointer flex-1">
                    {goal}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex gap-3 pt-4">
          {step > 1 && (
            <Button onClick={prevStep} variant="outline" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          )}
          {step < 4 ? (
            <Button onClick={nextStep} className="btn-glow gap-2 ml-auto">
              Next
              <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={loading || !formData.goal} className="btn-glow gap-2 ml-auto">
              {loading ? 'Saving...' : 'Complete Profile'}
              <CheckCircle className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
