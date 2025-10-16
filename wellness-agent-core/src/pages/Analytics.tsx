import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { BarChart3, TrendingUp, Download, Calendar, Apple, Activity, Flame } from 'lucide-react';

const Analytics = () => {
  const goals = [
    { name: 'Daily Calories', current: 1650, target: 2000, unit: 'kcal', color: 'from-warm to-orange-500' },
    { name: 'Protein Intake', current: 85, target: 100, unit: 'g', color: 'from-primary to-primary-glow' },
    { name: 'Water Consumption', current: 6, target: 8, unit: 'glasses', color: 'from-blue-400 to-blue-600' },
    { name: 'Exercise Minutes', current: 35, target: 60, unit: 'min', color: 'from-secondary to-green-500' },
  ];

  const weeklyData = [
    { day: 'Mon', calories: 1850, protein: 92, carbs: 220, fat: 65 },
    { day: 'Tue', calories: 1920, protein: 88, carbs: 235, fat: 68 },
    { day: 'Wed', calories: 1780, protein: 95, carbs: 210, fat: 62 },
    { day: 'Thu', calories: 2050, protein: 102, carbs: 245, fat: 72 },
    { day: 'Fri', calories: 1890, protein: 90, carbs: 225, fat: 66 },
    { day: 'Sat', calories: 2100, protein: 105, carbs: 250, fat: 75 },
    { day: 'Sun', calories: 1950, protein: 98, carbs: 230, fat: 70 },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 animate-fade-in">
          <div>
            <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
              <BarChart3 className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold mb-2 gradient-text">Nutritional Analytics</h1>
            <p className="text-lg text-muted-foreground">
              Track your progress and optimize your health journey
            </p>
          </div>
          <div className="flex gap-3 mt-4 md:mt-0">
            <Button variant="outline">
              <Calendar className="mr-2 h-4 w-4" />
              Last 7 Days
            </Button>
            <Button variant="hero">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </Button>
          </div>
        </div>

        {/* Goals Progress */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {goals.map((goal, index) => {
            const percentage = (goal.current / goal.target) * 100;
            return (
              <div
                key={goal.name}
                className="glass-card-elevated p-6 animate-scale-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-semibold text-sm text-muted-foreground">{goal.name}</h3>
                  <TrendingUp className="h-4 w-4 text-secondary" />
                </div>
                
                <div className="mb-4">
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-3xl font-bold">{goal.current}</span>
                    <span className="text-muted-foreground">/ {goal.target} {goal.unit}</span>
                  </div>
                  <Progress value={percentage} className="h-2" />
                </div>

                <div className={`w-full h-16 rounded-xl bg-gradient-to-br ${goal.color} opacity-20`} />
              </div>
            );
          })}
        </div>

        {/* Weekly Overview */}
        <div className="glass-card-elevated p-8 mb-8 animate-slide-up">
          <h2 className="text-2xl font-bold mb-6">Weekly Overview</h2>
          
          <div className="space-y-4">
            {weeklyData.map((day, index) => {
              const maxCalories = 2200;
              const caloriePercentage = (day.calories / maxCalories) * 100;
              
              return (
                <div key={day.day} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium w-16">{day.day}</span>
                    <div className="flex-1 mx-4">
                      <div className="h-8 bg-muted rounded-lg overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary via-accent to-warm rounded-lg transition-all duration-500 flex items-center justify-end px-3"
                          style={{ width: `${caloriePercentage}%` }}
                        >
                          <span className="text-xs font-semibold text-white">
                            {day.calories} kcal
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-4 text-xs">
                      <span className="text-primary">P: {day.protein}g</span>
                      <span className="text-accent">C: {day.carbs}g</span>
                      <span className="text-secondary">F: {day.fat}g</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Macro Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Nutrients Breakdown */}
          <div className="glass-card-elevated p-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Apple className="h-6 w-6 text-primary" />
              Macro Distribution
            </h3>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="font-medium">Protein</span>
                  <span className="text-primary font-bold">30%</span>
                </div>
                <Progress value={30} className="h-3 [&>div]:bg-primary" />
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="font-medium">Carbohydrates</span>
                  <span className="text-accent font-bold">45%</span>
                </div>
                <Progress value={45} className="h-3 [&>div]:bg-accent" />
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="font-medium">Fats</span>
                  <span className="text-secondary font-bold">25%</span>
                </div>
                <Progress value={25} className="h-3 [&>div]:bg-secondary" />
              </div>
            </div>

            <div className="mt-6 p-4 rounded-xl bg-muted/50">
              <p className="text-sm text-muted-foreground">
                Your macro distribution is well-balanced and aligns with recommended nutritional guidelines.
              </p>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="glass-card-elevated p-6 animate-slide-up" style={{ animationDelay: '200ms' }}>
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Activity className="h-6 w-6 text-primary" />
              Performance Metrics
            </h3>

            <div className="space-y-4">
              {[
                { label: 'Adherence to Plan', value: 92, icon: Flame, color: 'text-warm' },
                { label: 'Goal Achievement', value: 85, icon: TrendingUp, color: 'text-secondary' },
                { label: 'Nutritional Balance', value: 88, icon: Apple, color: 'text-primary' },
              ].map((metric) => {
                const Icon = metric.icon;
                return (
                  <div key={metric.label} className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-muted to-muted/50">
                      <Icon className={`h-6 w-6 ${metric.color}`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between mb-2">
                        <span className="font-medium text-sm">{metric.label}</span>
                        <span className="font-bold">{metric.value}%</span>
                      </div>
                      <Progress value={metric.value} className="h-2" />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 p-4 rounded-xl bg-gradient-to-br from-secondary/20 to-secondary/10 border border-secondary/20">
              <p className="text-sm font-medium text-secondary mb-1">Outstanding Progress!</p>
              <p className="text-sm text-muted-foreground">
                You're consistently meeting your health goals. Keep up the excellent work!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
