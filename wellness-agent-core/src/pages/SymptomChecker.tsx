import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Activity, Plus, X, AlertCircle, TrendingUp, Apple, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const SymptomChecker = () => {
  const [symptomInput, setSymptomInput] = useState('');
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [results, setResults] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const { toast } = useToast();

  const commonSymptoms = [
    'Headache', 'Fever', 'Fatigue', 'Cough', 'Nausea', 
    'Muscle Pain', 'Shortness of Breath', 'Dizziness'
  ];

  const addSymptom = (symptom: string) => {
    if (symptom && !symptoms.includes(symptom)) {
      setSymptoms([...symptoms, symptom]);
      setSymptomInput('');
    }
  };

  const removeSymptom = (symptom: string) => {
    setSymptoms(symptoms.filter(s => s !== symptom));
  };

  const analyzeSymptoms = () => {
    if (symptoms.length === 0) {
      toast({
        title: 'No symptoms entered',
        description: 'Please add at least one symptom to analyze.',
        variant: 'destructive',
      });
      return;
    }

    setIsAnalyzing(true);
    
    // Simulate AI analysis
    setTimeout(() => {
      setResults({
        conditions: [
          { 
            name: 'Common Cold',
            probability: 78,
            severity: 'Low',
            color: 'from-green-500 to-green-600',
            prevention: [
              'Get plenty of rest',
              'Stay hydrated',
              'Use over-the-counter cold medications',
              'Wash hands frequently'
            ]
          },
          {
            name: 'Seasonal Allergies',
            probability: 65,
            severity: 'Low',
            color: 'from-yellow-500 to-yellow-600',
            prevention: [
              'Avoid known allergens',
              'Use antihistamines',
              'Keep windows closed during high pollen days',
              'Consider consulting an allergist'
            ]
          },
          {
            name: 'Flu (Influenza)',
            probability: 42,
            severity: 'Medium',
            color: 'from-orange-500 to-orange-600',
            prevention: [
              'Get vaccinated annually',
              'Practice good hygiene',
              'Rest and stay home if sick',
              'Consult a doctor if symptoms worsen'
            ]
          }
        ]
      });
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
            <Activity className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-3 gradient-text">AI Symptom Checker</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Describe your symptoms and get AI-powered insights about possible conditions and recommendations
          </p>
        </div>

        {/* Symptom Input */}
        <div className="glass-card-elevated p-6 mb-6 animate-slide-up">
          <h2 className="text-xl font-semibold mb-4">Enter Your Symptoms</h2>
          
          <div className="flex gap-2 mb-4">
            <Input
              value={symptomInput}
              onChange={(e) => setSymptomInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addSymptom(symptomInput)}
              placeholder="Type a symptom (e.g., headache, fever)..."
              className="flex-1"
            />
            <Button onClick={() => addSymptom(symptomInput)} variant="hero">
              <Plus className="h-4 w-4 mr-2" />
              Add
            </Button>
          </div>

          {/* Quick Add Symptoms */}
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Common symptoms:</p>
            <div className="flex flex-wrap gap-2">
              {commonSymptoms.map((symptom) => (
                <Badge
                  key={symptom}
                  variant="outline"
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => addSymptom(symptom)}
                >
                  <Plus className="h-3 w-3 mr-1" />
                  {symptom}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {/* Selected Symptoms */}
        {symptoms.length > 0 && (
          <div className="glass-card p-6 mb-6 animate-scale-in">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Your Symptoms ({symptoms.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {symptoms.map((symptom) => (
                <Badge key={symptom} className="px-3 py-2 text-sm">
                  {symptom}
                  <button
                    onClick={() => removeSymptom(symptom)}
                    className="ml-2 hover:text-destructive transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
            
            <Button
              onClick={analyzeSymptoms}
              variant="hero"
              size="lg"
              className="w-full mt-6"
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <Sparkles className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing Symptoms...
                </>
              ) : (
                <>
                  <Activity className="mr-2 h-5 w-5" />
                  Analyze Symptoms
                </>
              )}
            </Button>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Analysis Results</h2>
              <Link to="/diet-plan">
                <Button variant="warm" className="btn-glow">
                  <Apple className="mr-2 h-4 w-4" />
                  Get Diet Plan
                </Button>
              </Link>
            </div>

            {results.conditions.map((condition: any, index: number) => (
              <div
                key={condition.name}
                className="glass-card-elevated p-6 animate-slide-up"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2">{condition.name}</h3>
                    <div className="flex items-center gap-4">
                      <Badge
                        className={`${
                          condition.severity === 'Low' 
                            ? 'bg-secondary' 
                            : condition.severity === 'Medium'
                            ? 'bg-warm'
                            : 'bg-destructive'
                        }`}
                      >
                        {condition.severity} Severity
                      </Badge>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <TrendingUp className="h-4 w-4" />
                        <span className="text-sm">{condition.probability}% match</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">Probability</span>
                    <span className="font-semibold">{condition.probability}%</span>
                  </div>
                  <Progress value={condition.probability} className="h-3" />
                </div>

                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-primary" />
                    Prevention & Care Tips
                  </h4>
                  <ul className="space-y-2">
                    {condition.prevention.map((tip: string, i: number) => (
                      <li key={i} className="flex items-start gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-primary mt-2 shrink-0" />
                        <span className="text-muted-foreground">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}

            {/* Disclaimer */}
            <div className="glass-card p-6 border-l-4 border-warm">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Important:</strong> This AI analysis is for informational purposes only 
                and should not replace professional medical advice. If symptoms persist or worsen, please consult a healthcare provider.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SymptomChecker;
