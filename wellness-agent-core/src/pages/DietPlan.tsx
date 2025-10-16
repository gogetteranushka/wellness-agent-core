import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Apple, ChevronLeft, ChevronRight, RefreshCw, Download, 
  Printer, ChefHat, Clock, Flame, Leaf 
} from 'lucide-react';

const DietPlan = () => {
  const [currentDay, setCurrentDay] = useState(0);
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const meals = {
    breakfast: {
      name: 'Protein-Packed Smoothie Bowl',
      time: '8:00 AM',
      calories: 420,
      protein: 28,
      carbs: 52,
      fat: 12,
      ingredients: ['Greek yogurt', 'Banana', 'Berries', 'Chia seeds', 'Almond butter', 'Granola'],
      tags: ['High Protein', 'Vegetarian', 'Quick'],
    },
    lunch: {
      name: 'Quinoa Buddha Bowl',
      time: '12:30 PM',
      calories: 580,
      protein: 22,
      carbs: 68,
      fat: 24,
      ingredients: ['Quinoa', 'Chickpeas', 'Avocado', 'Roasted vegetables', 'Tahini dressing'],
      tags: ['Vegan', 'High Fiber', 'Low Sodium'],
    },
    dinner: {
      name: 'Grilled Salmon with Vegetables',
      time: '7:00 PM',
      calories: 520,
      protein: 42,
      carbs: 35,
      fat: 22,
      ingredients: ['Wild salmon', 'Sweet potato', 'Broccoli', 'Asparagus', 'Lemon', 'Olive oil'],
      tags: ['High Protein', 'Omega-3', 'Heart Healthy'],
    },
    snack: {
      name: 'Mixed Nuts & Fruit',
      time: '3:00 PM',
      calories: 240,
      protein: 8,
      carbs: 28,
      fat: 12,
      ingredients: ['Almonds', 'Walnuts', 'Apple slices', 'Dried cranberries'],
      tags: ['Quick', 'Portable'],
    },
  };

  const dailyTotals = {
    calories: 1760,
    protein: 100,
    carbs: 183,
    fat: 70,
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-warm mb-4 shadow-glow">
            <Apple className="h-10 w-10 text-foreground" />
          </div>
          <h1 className="text-4xl font-bold mb-3 gradient-text">AI Diet Plan</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Personalized meal plans tailored to your health goals and dietary preferences
          </p>
        </div>

        {/* Day Navigator */}
        <div className="glass-card-elevated p-4 mb-6 animate-slide-up">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCurrentDay(Math.max(0, currentDay - 1))}
              disabled={currentDay === 0}
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>

            <div className="flex-1 flex justify-center gap-2 overflow-x-auto">
              {days.map((day, index) => (
                <button
                  key={day}
                  onClick={() => setCurrentDay(index)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    currentDay === index
                      ? 'bg-gradient-to-r from-primary to-accent text-white shadow-glow'
                      : 'hover:bg-muted'
                  }`}
                >
                  {day}
                </button>
              ))}
            </div>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCurrentDay(Math.min(days.length - 1, currentDay + 1))}
              disabled={currentDay === days.length - 1}
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-3 mb-6 justify-center">
          <Button variant="hero">
            <RefreshCw className="mr-2 h-4 w-4" />
            Regenerate Plan
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
          <Button variant="outline">
            <Printer className="mr-2 h-4 w-4" />
            Print
          </Button>
        </div>

        {/* Meals Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {Object.entries(meals).map(([mealType, meal], index) => (
            <div
              key={mealType}
              className="glass-card-elevated group hover:scale-[1.02] transition-all duration-300 animate-scale-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <ChefHat className="h-5 w-5 text-primary" />
                      <span className="text-sm font-medium text-muted-foreground uppercase">
                        {mealType}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold mb-1">{meal.name}</h3>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      <span>{meal.time}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>

                {/* Nutrition Info */}
                <div className="grid grid-cols-4 gap-2 mb-4 p-4 rounded-xl bg-muted/50">
                  <div className="text-center">
                    <Flame className="h-4 w-4 mx-auto mb-1 text-warm" />
                    <p className="text-xs text-muted-foreground">Calories</p>
                    <p className="font-bold">{meal.calories}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground mb-1">Protein</p>
                    <p className="font-bold text-primary">{meal.protein}g</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground mb-1">Carbs</p>
                    <p className="font-bold text-accent">{meal.carbs}g</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground mb-1">Fat</p>
                    <p className="font-bold text-secondary">{meal.fat}g</p>
                  </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {meal.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>

                {/* Ingredients */}
                <Tabs defaultValue="ingredients" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="ingredients">Ingredients</TabsTrigger>
                    <TabsTrigger value="instructions">Steps</TabsTrigger>
                  </TabsList>
                  <TabsContent value="ingredients" className="mt-4">
                    <ul className="space-y-2">
                      {meal.ingredients.map((ingredient, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <Leaf className="h-3 w-3 text-secondary shrink-0" />
                          <span className="text-sm text-muted-foreground">{ingredient}</span>
                        </li>
                      ))}
                    </ul>
                  </TabsContent>
                  <TabsContent value="instructions" className="mt-4">
                    <p className="text-sm text-muted-foreground">
                      Detailed cooking instructions will be displayed here...
                    </p>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          ))}
        </div>

        {/* Daily Summary */}
        <div className="glass-card-elevated p-6 animate-fade-in">
          <h3 className="text-xl font-bold mb-6">Daily Nutritional Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 rounded-xl bg-gradient-to-br from-warm/20 to-warm/10">
              <Flame className="h-8 w-8 mx-auto mb-2 text-warm" />
              <p className="text-sm text-muted-foreground mb-1">Total Calories</p>
              <p className="text-2xl font-bold">{dailyTotals.calories}</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-gradient-to-br from-primary/20 to-primary/10">
              <p className="text-sm text-muted-foreground mb-1">Protein</p>
              <p className="text-2xl font-bold text-primary">{dailyTotals.protein}g</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-gradient-to-br from-accent/20 to-accent/10">
              <p className="text-sm text-muted-foreground mb-1">Carbs</p>
              <p className="text-2xl font-bold text-accent">{dailyTotals.carbs}g</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-gradient-to-br from-secondary/20 to-secondary/10">
              <p className="text-sm text-muted-foreground mb-1">Fat</p>
              <p className="text-2xl font-bold text-secondary">{dailyTotals.fat}g</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DietPlan;
