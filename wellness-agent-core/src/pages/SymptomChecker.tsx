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
  const [searchTerm, setSearchTerm] = useState(''); // NEW

  useEffect(() => {
    // Fetch available symptoms from backend
    fetch('http://localhost:5000/api/symptoms')
      .then((res) => res.json())
      .then((data) => {
        setAvailableSymptoms(data.symptoms || []);
        setFetchingSymptoms(false);
      })
      .catch((err) => {
        console.error('Error fetching symptoms:', err);
        setFetchingSymptoms(false);
      });
  }, []);

  const toggleSymptom = (symptom: string) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter((s) => s !== symptom));
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
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const response = await fetch('http://localhost:5000/api/symptom-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ symptoms: selectedSymptoms }),
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
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  // NON-STRICT, CASE-INSENSITIVE FILTER
  const filteredSymptoms = availableSymptoms.filter((symptom) =>
    symptom.toLowerCase().includes(searchTerm.toLowerCase().trim()),
  );

  if (fetchingSymptoms) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="glass-card p-6 md:p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 rounded-xl bg-primary/10">
            <Activity className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold">
              AI Symptom Checker
            </h1>
            <p className="text-sm text-muted-foreground">
              Select your symptoms from the list below to get AI-powered health
              insights
            </p>
          </div>
        </div>

        {/* Symptom Selection */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold">Select Your Symptoms</h2>
            <Badge variant="outline">
              {selectedSymptoms.length} symptom(s) selected
            </Badge>
          </div>

          {/* SEARCH BAR */}
          <div className="mb-3">
            <input
              type="text"
              placeholder="Search symptoms (e.g., headache, chest pain)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="max-h-64 overflow-y-auto border rounded-lg p-3 bg-muted/30">
            {filteredSymptoms.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No symptoms match your search.
              </p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {filteredSymptoms.map((symptom) => (
                  <label
                    key={symptom}
                    className="flex items-center space-x-2 text-sm cursor-pointer p-2 rounded-md hover:bg-muted"
                  >
                    <Checkbox
                      checked={selectedSymptoms.includes(symptom)}
                      onCheckedChange={() => toggleSymptom(symptom)}
                    />
                    <span>{symptom}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="mt-4 flex justify-end">
            <Button onClick={analyzeSymptoms} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze Symptoms'
              )}
            </Button>
          </div>
        </div>

        {/* Results */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-3">Analysis Results</h2>
          {!results ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <AlertCircle className="h-4 w-4" />
              <span>Select symptoms and click "Analyze" to see results.</span>
            </div>
          ) : (
            <div className="space-y-4">
              {results.conditions?.map((condition: any, index: number) => (
                <div
                  key={index}
                  className="border rounded-lg p-4 flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-primary" />
                      <span className="font-semibold">
                        {condition.name}
                      </span>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(
                        condition.severity,
                      )}`}
                    >
                      {condition.severity} risk
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Confidence: {condition.probability}%
                  </p>
                  <div className="mt-2">
                    <p className="text-sm font-medium mb-1">Recommendations:</p>
                    <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                      {condition.prevention.map(
                        (item: string, idx: number) => (
                          <li key={idx}>{item}</li>
                        ),
                      )}
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
