import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Activity, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { supabase } from '../../supabaseClient';

const SymptomChecker = () => {
  const [availableSymptoms, setAvailableSymptoms] = useState<string[]>([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [fetchingSymptoms, setFetchingSymptoms] = useState(true);

  useEffect(() => {
    // Fetch available symptoms from backend
    fetch('http://localhost:5000/api/symptoms')
      .then(res => res.json())
      .then(data => {
        setAvailableSymptoms(data.symptoms || []);
        setFetchingSymptoms(false);
      })
      .catch(err => {
        console.error('Error fetching symptoms:', err);
        setFetchingSymptoms(false);
      });
  }, []);

  const toggleSymptom = (symptom: string) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
    } else {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
  };

  const analyzeSymptoms = async () => {
    if (selectedSymptoms.length === 0) {
      alert('Please select at least one symptom');
      return;
    }

    setLoading(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const response = await fetch('http://localhost:5000/api/symptom-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({ symptoms: selectedSymptoms })
      });

      const data = await response.json();
      setResults(data.result);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to analyze symptoms');
    }
    setLoading(false);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-orange-100 text-orange-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  if (fetchingSymptoms) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Activity className="h-8 w-8" />
          AI Symptom Checker
        </h1>
        <p className="text-muted-foreground">
          Select your symptoms from the list below to get AI-powered health insights
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Symptom Selection */}
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Select Your Symptoms</h2>
          <p className="text-sm text-muted-foreground mb-4">
            {selectedSymptoms.length} symptom(s) selected
          </p>
          
          <div className="max-h-96 overflow-y-auto space-y-2 pr-2">
            {availableSymptoms.map((symptom) => (
              <div
                key={symptom}
                className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 cursor-pointer"
                onClick={() => toggleSymptom(symptom)}
              >
                <Checkbox
                  checked={selectedSymptoms.includes(symptom)}
                  onCheckedChange={() => toggleSymptom(symptom)}
                />
                <label className="text-sm cursor-pointer flex-1">
                  {symptom}
                </label>
              </div>
            ))}
          </div>

          <Button
            onClick={analyzeSymptoms}
            disabled={loading || selectedSymptoms.length === 0}
            className="w-full mt-4"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              'Analyze Symptoms'
            )}
          </Button>
        </div>

        {/* Results */}
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
          
          {!results ? (
            <div className="text-center py-12 text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select symptoms and click "Analyze" to see results</p>
            </div>
          ) : (
            <div className="space-y-4">
              {results.conditions.map((condition: any, index: number) => (
                <div key={index} className="glass-card p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-lg">{condition.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        Confidence: {condition.probability}%
                      </p>
                    </div>
                    <Badge className={getSeverityColor(condition.severity)}>
                      {condition.severity}
                    </Badge>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium mb-2">Recommendations:</h4>
                    <ul className="space-y-1">
                      {condition.prevention.map((item: string, idx: number) => (
                        <li key={idx} className="text-sm flex items-start gap-2">
                          <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SymptomChecker;
