import { useState } from 'react';
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

  const steps = [
    { number: 1, title: 'Demographics', icon: User, color: 'from-primary to-primary-glow' },
    { number: 2, title: 'Medical History', icon: Heart, color: 'from-secondary to-green-400' },
    { number: 3, title: 'Lifestyle', icon: Activity, color: 'from-accent to-purple-400' },
  ];

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    }
  };

  const handlePrevious = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = () => {
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
          <p className="text-muted-foreground mb-6">
            Help us personalize your wellness journey
          </p>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground mb-2">
              <span>Step {step} of {totalSteps}</span>
              <span>{Math.round((step / totalSteps) * 100)}% Complete</span>
            </div>
            <Progress value={(step / totalSteps) * 100} className="h-2" />
          </div>

          {/* Step Indicators */}
          <div className="flex justify-between mt-6">
            {steps.map((s) => {
              const Icon = s.icon;
              const isActive = step === s.number;
              const isCompleted = step > s.number;
              
              return (
                <div
                  key={s.number}
                  className={`flex flex-col items-center flex-1 ${
                    isActive ? 'animate-scale-in' : ''
                  }`}
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all ${
                      isCompleted
                        ? 'bg-secondary text-secondary-foreground'
                        : isActive
                        ? `bg-gradient-to-br ${s.color} text-white shadow-glow`
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {isCompleted ? <Check className="h-6 w-6" /> : <Icon className="h-6 w-6" />}
                  </div>
                  <span className={`text-sm font-medium ${isActive ? 'text-foreground' : 'text-muted-foreground'}`}>
                    {s.title}
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
                <div className={`p-3 rounded-xl bg-gradient-to-br ${steps[0].color}`}>
                  <User className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold">Demographics</h2>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Age</Label>
                  <Input type="number" placeholder="32" />
                </div>
                <div className="space-y-2">
                  <Label>Gender</Label>
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm">
                    <option>Female</option>
                    <option>Male</option>
                    <option>Other</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Height (cm)</Label>
                  <Input type="number" placeholder="168" />
                </div>
                <div className="space-y-2">
                  <Label>Weight (kg)</Label>
                  <Input type="number" placeholder="66" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Blood Type</Label>
                <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm">
                  <option>O+</option>
                  <option>O-</option>
                  <option>A+</option>
                  <option>A-</option>
                  <option>B+</option>
                  <option>B-</option>
                  <option>AB+</option>
                  <option>AB-</option>
                </select>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${steps[1].color}`}>
                  <Heart className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold">Medical History</h2>
              </div>

              <div className="space-y-2">
                <Label>Existing Conditions</Label>
                <Textarea 
                  placeholder="List any existing medical conditions (e.g., diabetes, hypertension)..."
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label>Allergies</Label>
                <Input placeholder="e.g., Peanuts, Shellfish, Pollen" />
              </div>

              <div className="space-y-2">
                <Label>Current Medications</Label>
                <Textarea 
                  placeholder="List any medications you're currently taking..."
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
                <div className={`p-3 rounded-xl bg-gradient-to-br ${steps[2].color}`}>
                  <Activity className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold">Lifestyle</h2>
              </div>

              <div className="space-y-2">
                <Label>Exercise Frequency</Label>
                <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm">
                  <option>Daily</option>
                  <option>4-5 times per week</option>
                  <option>2-3 times per week</option>
                  <option>Once a week</option>
                  <option>Rarely</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Diet Type</Label>
                <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm">
                  <option>Vegetarian</option>
                  <option>Vegan</option>
                  <option>Pescatarian</option>
                  <option>No restrictions</option>
                  <option>Other</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Dietary Preferences</Label>
                <Input placeholder="e.g., Low sodium, Organic, Gluten-free" />
              </div>

              <div className="space-y-2">
                <Label>Average Sleep (hours)</Label>
                <Input type="number" placeholder="7-8" />
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
