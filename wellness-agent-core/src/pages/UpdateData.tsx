import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { User, Heart, Activity, Upload, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const UpdateData = () => {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const { toast } = useToast();
  const totalSteps = 3;

  // Form state placeholders; enhance with real form state logic as needed
  const [demographics, setDemographics] = useState({
    age: '',
    gender: 'Female',
    height: '',
    weight: '',
    bloodType: 'O+',
  });
  const [medicalHistory, setMedicalHistory] = useState({
    existingConditions: '',
    allergies: '',
    medications: '',
  });
  const [lifestyle, setLifestyle] = useState({
    exerciseFrequency: 'Daily',
    dietType: 'Vegetarian',
    dietaryPreferences: '',
    avgSleep: '',
  });

  const handleNext = () => {
    // Add validation before advancing if needed
    setStep((prev) => Math.min(totalSteps, prev + 1));
  };

  const handlePrevious = () => {
    setStep((prev) => Math.max(1, prev - 1));
  };

  const handleSubmit = () => {
    // TODO: validate and submit all data to backend here
    toast({
      title: 'Profile updated!',
      description: 'Your health data has been successfully saved.',
    });
    navigate('/profile');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        {/* Progress Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold mb-2">Update Your Health Data</h1>
          <p className="text-muted-foreground mb-6">Help us personalize your wellness journey</p>

          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground mb-2">
              <span>Step {step} of {totalSteps}</span>
              <span>{Math.round((step / totalSteps) * 100)}% Complete</span>
            </div>
            <Progress value={(step / totalSteps) * 100} className="h-2" />
          </div>

          {/* Step Indicators */}
          <div className="flex justify-between mt-6">
            {[1, 2, 3].map((s) => {
              const isActive = step === s;
              const isCompleted = step > s;
              const icons = [User, Heart, Activity];
              const colors = ['from-primary to-primary-glow', 'from-secondary to-green-400', 'from-accent to-purple-400'];
              const Icon = icons[s - 1];

              return (
                <div
                  key={s}
                  className={`flex flex-col items-center flex-1 ${isActive ? 'animate-scale-in' : ''}`}
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all ${
                      isCompleted
                        ? 'bg-secondary text-secondary-foreground'
                        : isActive
                        ? `bg-gradient-to-br ${colors[s - 1]} text-white shadow-glow`
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {isCompleted ? <Check className="h-6 w-6" /> : <Icon className="h-6 w-6" />}
                  </div>
                  <span className={`text-sm font-medium ${isActive ? 'text-foreground' : 'text-muted-foreground'}`}>
                    {['Demographics', 'Medical History', 'Lifestyle'][s - 1]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Form */}
        <div className="glass-card-elevated p-8 animate-slide-up">
          {step === 1 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gradient-to-br from-primary to-primary-glow">
                  <User className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold">Demographics</h2>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Age</Label>
                  <Input
                    type="number"
                    placeholder="32"
                    value={demographics.age}
                    onChange={(e) => setDemographics({...demographics, age: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Gender</Label>
                  <select
                    className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                    value={demographics.gender}
                    onChange={(e) => setDemographics({...demographics, gender: e.target.value})}
                  >
                    <option>Female</option>
                    <option>Male</option>
                    <option>Other</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Height (cm)</Label>
                  <Input
                    type="number"
                    placeholder="168"
                    value={demographics.height}
                    onChange={(e) => setDemographics({...demographics, height: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Weight (kg)</Label>
                  <Input
                    type="number"
                    placeholder="66"
                    value={demographics.weight}
                    onChange={(e) => setDemographics({...demographics, weight: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Blood Type</Label>
                <select
                  className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                  value={demographics.bloodType}
                  onChange={(e) => setDemographics({...demographics, bloodType: e.target.value})}
                >
                  {['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'].map((bt) => (
                    <option key={bt} value={bt}>{bt}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gradient-to-br from-secondary to-green-400">
                  <Heart className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold">Medical History</h2>
              </div>

              <div className="space-y-2">
                <Label>Existing Conditions</Label>
                <Textarea
                  placeholder="List any existing medical conditions (e.g., diabetes, hypertension)..."
                  value={medicalHistory.existingConditions}
                  onChange={(e) => setMedicalHistory({...medicalHistory, existingConditions: e.target.value})}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label>Allergies</Label>
                <Input
                  placeholder="e.g., Peanuts, Shellfish, Pollen"
                  value={medicalHistory.allergies}
                  onChange={(e) => setMedicalHistory({...medicalHistory, allergies: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label>Current Medications</Label>
                <Textarea
                  placeholder="List any medications you're currently taking..."
                  value={medicalHistory.medications}
                  onChange={(e) => setMedicalHistory({...medicalHistory, medications: e.target.value})}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label>Upload Medical Records (CSV)</Label>
                <div className="border-2 border-dashed border-border rounded-xl p-8 text-center hover:border-primary transition-colors cursor-pointer">
                  <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Drag and drop your CSV file here, or click to browse
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Supported format: CSV (Max 10MB)
                  </p>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gradient-to-br from-accent to-purple-400">
                  <Activity className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold">Lifestyle</h2>
              </div>

              <div className="space-y-2">
                <Label>Exercise Frequency</Label>
                <select
                  className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                  value={lifestyle.exerciseFrequency}
                  onChange={(e) => setLifestyle({...lifestyle, exerciseFrequency: e.target.value})}
                >
                  <option>Daily</option>
                  <option>4-5 times per week</option>
                  <option>2-3 times per week</option>
                  <option>Once a week</option>
                  <option>Rarely</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Diet Type</Label>
                <select
                  className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                  value={lifestyle.dietType}
                  onChange={(e) => setLifestyle({...lifestyle, dietType: e.target.value})}
                >
                  <option>Vegetarian</option>
                  <option>Vegan</option>
                  <option>Pescatarian</option>
                  <option>No restrictions</option>
                  <option>Other</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Dietary Preferences</Label>
                <Input
                  placeholder="e.g., Low sodium, Organic, Gluten-free"
                  value={lifestyle.dietaryPreferences}
                  onChange={(e) => setLifestyle({...lifestyle, dietaryPreferences: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label>Average Sleep (hours)</Label>
                <Input
                  type="number"
                  placeholder="7-8"
                  value={lifestyle.avgSleep}
                  onChange={(e) => setLifestyle({...lifestyle, avgSleep: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label>Wearable Device Integration</Label>
                <div className="p-4 rounded-xl bg-muted/50 flex items-center justify-between">
                  <div>
                    <p className="font-medium mb-1">Connect Your Device</p>
                    <p className="text-sm text-muted-foreground">
                      Sync data from fitness trackers and smartwatches
                    </p>
                  </div>
                  <Button variant="outline">Connect</Button>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-3 mt-8 pt-6 border-t border-border">
            {step > 1 && (
              <Button variant="outline" onClick={handlePrevious} className="flex-1">
                Previous
              </Button>
            )}
            {step < totalSteps ? (
              <Button variant="hero" onClick={handleNext} className="flex-1">
                Next Step
              </Button>
            ) : (
              <Button variant="hero" onClick={handleSubmit} className="flex-1">
                Save & Complete
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UpdateData;
