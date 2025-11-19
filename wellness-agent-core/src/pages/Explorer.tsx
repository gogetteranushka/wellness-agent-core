import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Book,
  Search,
  Heart,
  Apple,
  Leaf,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { supabase } from '../../supabaseClient';

const Explorer = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCondition, setSelectedCondition] = useState('Type 2 Diabetes');
  const [conditions, setConditions] = useState([
    'Type 2 Diabetes',
    'Hypertension',
    'High Cholesterol',
    'Anemia',
    'Osteoporosis',
    'Heart Disease',
    'Digestive Issues',
  ]);
  const [nutrients, setNutrients] = useState([
    {
      name: 'Fiber',
      benefit: 'Helps regulate blood sugar levels',
      warning: null,
      icon: Leaf,
      color: 'from-secondary to-green-500',
    },
    {
      name: 'Magnesium',
      benefit: 'Improves insulin sensitivity',
      warning: null,
      icon: CheckCircle,
      color: 'from-blue-400 to-blue-600',
    },
    {
      name: 'Omega-3',
      benefit: 'Reduces inflammation',
      warning: 'Consult doctor if on blood thinners',
      icon: Heart,
      color: 'from-primary to-primary-glow',
    },
    {
      name: 'Vitamin D',
      benefit: 'Supports insulin function',
      warning: null,
      icon: CheckCircle,
      color: 'from-warm to-orange-500',
    },
  ]);
  const [foods, setFoods] = useState([
    {
      name: 'Quinoa',
      category: 'Whole Grains',
      benefits: ['High in fiber', 'Low glycemic index', 'Rich in protein'],
      nutrients: ['Fiber', 'Magnesium', 'Protein'],
    },
    {
      name: 'Salmon',
      category: 'Fish',
      benefits: ['Rich in Omega-3', 'High protein', 'Anti-inflammatory'],
      nutrients: ['Omega-3', 'Vitamin D', 'Protein'],
    },
    {
      name: 'Spinach',
      category: 'Leafy Greens',
      benefits: ['Low calorie', 'High in vitamins', 'Antioxidant-rich'],
      nutrients: ['Fiber', 'Magnesium', 'Vitamin A'],
    },
    {
      name: 'Almonds',
      category: 'Nuts',
      benefits: ['Heart healthy', 'Blood sugar control', 'Satisfying'],
      nutrients: ['Fiber', 'Magnesium', 'Healthy fats'],
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Example: If you want to load real data for these lists, use an effect:
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;

        // Fetch conditions from backend API (example URL, replace with real)
        // const resConditions = await fetch('http://localhost:5000/api/conditions', { headers: { Authorization: `Bearer ${token}` } });
        // const condData = await resConditions.json();
        // setConditions(condData);

        // Similarly, fetch nutrients and foods

      } catch (err: any) {
        setError(err.message);
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-accent to-purple-500 mb-4 shadow-glow">
            <Book className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-3 gradient-text">Condition Explorer</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Discover the relationship between health conditions, nutrients, and foods
          </p>
          {loading && <p>Loading data...</p>}
          {error && <p className="text-red-600">{error}</p>}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Conditions Sidebar */}
          <div className="lg:col-span-1">
            <div className="glass-card-elevated p-6 sticky top-24 animate-slide-up">
              <h2 className="text-xl font-bold mb-4">Conditions</h2>

              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search conditions..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                {conditions
                  .filter((c) => c.toLowerCase().includes(searchQuery.toLowerCase()))
                  .map((condition) => (
                    <button
                      key={condition}
                      onClick={() => setSelectedCondition(condition)}
                      className={`w-full text-left p-3 rounded-lg transition-all ${
                        selectedCondition === condition
                          ? 'bg-gradient-to-r from-primary to-accent text-white shadow-glow'
                          : 'hover:bg-muted'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Heart className="h-4 w-4 shrink-0" />
                        <span className="text-sm font-medium">{condition}</span>
                      </div>
                    </button>
                  ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8">
            {/* Condition Info */}
            <div className="glass-card-elevated p-8 animate-fade-in">
              <h2 className="text-3xl font-bold mb-4">{selectedCondition}</h2>
              <p className="text-muted-foreground mb-6">
                Understanding key nutrients and foods that can help manage this condition through diet.
              </p>

              <div className="flex flex-wrap gap-2">
                <Badge className="bg-primary">Manageable with Diet</Badge>
                <Badge variant="secondary">Evidence-Based</Badge>
                <Badge variant="outline">Consult Healthcare Provider</Badge>
              </div>
            </div>

            {/* Key Nutrients */}
            <div className="animate-slide-up">
              <h3 className="text-2xl font-bold mb-6">Key Nutrients</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {nutrients.map((nutrient, index) => {
                  const Icon = nutrient.icon;
                  return (
                    <div
                      key={nutrient.name}
                      className="glass-card p-6 hover:scale-[1.02] transition-all"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-xl bg-gradient-to-br ${nutrient.color} shrink-0`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-bold mb-2">{nutrient.name}</h4>
                          <div className="space-y-2">
                            <div className="flex items-start gap-2">
                              <CheckCircle className="h-4 w-4 text-secondary shrink-0 mt-0.5" />
                              <p className="text-sm text-muted-foreground">{nutrient.benefit}</p>
                            </div>
                            {nutrient.warning && (
                              <div className="flex items-start gap-2">
                                <AlertCircle className="h-4 w-4 text-warm shrink-0 mt-0.5" />
                                <p className="text-sm text-muted-foreground">{nutrient.warning}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Recommended Foods */}
            <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
              <h3 className="text-2xl font-bold mb-6">Recommended Foods</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {foods.map((food) => (
                  <div key={food.name} className="glass-card-elevated p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h4 className="text-xl font-bold mb-1">{food.name}</h4>
                        <Badge variant="secondary" className="text-xs">
                          <Apple className="h-3 w-3 mr-1" />
                          {food.category}
                        </Badge>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-semibold mb-2">Benefits:</p>
                        <ul className="space-y-1">
                          {food.benefits.map((benefit, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                              <CheckCircle className="h-3.5 w-3.5 text-secondary shrink-0 mt-0.5" />
                              {benefit}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <p className="text-sm font-semibold mb-2">Key Nutrients:</p>
                        <div className="flex flex-wrap gap-2">
                          {food.nutrients.map((nutrient) => (
                            <Badge key={nutrient} variant="outline" className="text-xs">
                              {nutrient}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Glossary Note */}
            <div className="glass-card p-6 border-l-4 border-primary">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Book className="h-5 w-5 text-primary" />
                Glossary & Resources
              </h4>
              <p className="text-sm text-muted-foreground">
                Click on any nutrient or food term to view detailed explanations, sources, and scientific research supporting these recommendations.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Explorer;
