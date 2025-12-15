import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Loader2,
  Dumbbell,
  CheckCircle,
  Calendar,
  Clock,
  Zap,
  Heart,
  TrendingUp,
  AlertCircle,
} from "lucide-react";
import { supabase } from "../../supabaseClient";
import { useToast } from "@/hooks/use-toast";

type WorkoutPrefs = {
  goal: string;
  experience_level: string;
  days_per_week: number;
  session_length_mins: number;
  equipment: string[];
  preferred_env: string | null;
  injuries: string[];
  cardio_preference: string | null;
  workout_style: string;
  notes: string | null;
};

type WeeklyPlan = {
  weekly_plan: {
    [day: string]: "rest" | any[];
  };
  guidelines?: string[];
};

const WorkoutPlan: React.FC = () => {
  const { toast } = useToast();

  // LLM parser state
  const [preferenceText, setPreferenceText] = useState("");
  const [parsing, setParsing] = useState(false);
  const [parsedPreview, setParsedPreview] = useState<WorkoutPrefs | null>(null);

  // Manual/basic state
  const [prefs, setPrefs] = useState<WorkoutPrefs>({
    goal: "general_health",
    experience_level: "beginner",
    days_per_week: 3,
    session_length_mins: 30,
    equipment: ["bodyweight"],
    preferred_env: null,
    injuries: [],
    cardio_preference: null,
    workout_style: "full_body",
    notes: null,
  });

  const [weeklyPlan, setWeeklyPlan] = useState<WeeklyPlan | null>(null);
  const [generating, setGenerating] = useState(false);

  // ------------------------------------------------------------------
  // CALL /api/workout/parse-preferences-text
  // ------------------------------------------------------------------
  const handleParsePreferences = async () => {
    if (!preferenceText.trim()) {
      toast({
        title: "Empty Input",
        description: "Please describe your workout preferences first.",
        variant: "destructive",
      });
      return;
    }

    setParsing(true);
    try {
      const { data: sessionData } = await supabase.auth.getSession();

      const res = await fetch(
        "http://localhost:5000/api/workout/parse-preferences-text",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${sessionData?.session?.access_token ?? ""}`,
          },
          body: JSON.stringify({
            text: preferenceText,
            defaults: prefs,
          }),
        }
      );

      const data = await res.json();

      if (data.status === "success") {
        const structured: WorkoutPrefs = data.data.structured;

        setPrefs(structured);
        setParsedPreview(structured);

        toast({
          title: "✨ Workout Preferences Understood",
          description: `Extracted ${
            Object.keys(structured).filter(
              (k) => (structured as any)[k] !== null
            ).length
          } fields from your text.`,
        });

        console.log("Parsed workout prefs:", structured);
      } else {
        throw new Error(data.message || "Failed to parse workout preferences");
      }
    } catch (err: any) {
      console.error("Workout parse error:", err);
      toast({
        title: "Parsing Failed",
        description:
          err?.message ||
          "Could not interpret your text. Please try again or use the manual options.",
        variant: "destructive",
      });
    } finally {
      setParsing(false);
    }
  };

  // ------------------------------------------------------------------
  // CALL /api/workout/complete-plan
  // ------------------------------------------------------------------
  const handleGeneratePlan = async () => {
    setGenerating(true);
    setWeeklyPlan(null);

    try {
      const { data: sessionData } = await supabase.auth.getSession();

      const payload = {
        user_profile: {},
        workout_preferences: parsedPreview ?? prefs,
      };

      const res = await fetch(
        "http://localhost:5000/api/workout/complete-plan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${sessionData?.session?.access_token ?? ""}`,
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await res.json();
      if (data.status === "success") {
        setWeeklyPlan(data.data);
        toast({
          title: "Workout Plan Ready",
          description: "Your weekly workout schedule has been generated.",
        });
      } else {
        throw new Error(data.message || "Failed to generate workout plan");
      }
    } catch (err: any) {
      console.error("Workout plan error:", err);
      toast({
        title: "Error",
        description: err?.message || "Failed to generate workout plan.",
        variant: "destructive",
      });
    } finally {
      setGenerating(false);
    }
  };

  // Helper to format day name
  const formatDay = (day: string) =>
    day.charAt(0).toUpperCase() + day.slice(1);

  // Goal display mapping
  const goalLabels: Record<string, { label: string; icon: any; color: string }> = {
    weight_loss: { label: "Fat Loss", icon: TrendingUp, color: "text-red-500" },
    muscle_gain: { label: "Muscle Gain", icon: Dumbbell, color: "text-blue-500" },
    general_health: { label: "General Health", icon: Heart, color: "text-green-500" },
    maintenance: { label: "Maintenance", icon: Zap, color: "text-yellow-500" },
  };

  // ------------------------------------------------------------------
  // RENDER
  // ------------------------------------------------------------------

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 mb-4 shadow-lg">
            <Dumbbell className="h-12 w-12 text-white" />
          </div>
          <h1 className="text-5xl font-bold mb-3 bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            AI Workout Plan
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Get a science-backed weekly workout schedule tailored to your goals,
            equipment, and experience level.
          </p>
        </div>

        {/* AI Parser Card */}
        <div className="glass-card p-8 mb-6 border-2 border-purple-200 dark:border-purple-800">
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-3">
              <Sparkles className="h-6 w-6 text-purple-600" />
              <Label className="text-xl font-semibold">
                AI Workout Preference Parser
              </Label>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              Describe your workout situation in plain English. Our AI will
              extract your goals, experience level, available equipment, and
              constraints.
            </p>
            <textarea
              value={preferenceText}
              onChange={(e) => setPreferenceText(e.target.value)}
              placeholder="Example: I'm a complete beginner, want to lose fat, can train 3 days a week at home with just bodyweight. I have bad knees, so I prefer walking over running for cardio."
              className="w-full min-h-[140px] p-4 rounded-lg border-2 border-input bg-background/50 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              disabled={parsing}
            />
            <Button
              onClick={handleParsePreferences}
              disabled={parsing || !preferenceText.trim()}
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg"
              size="lg"
            >
              {parsing ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Interpreting Workout Preferences...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  Interpret My Preferences
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Parsed Preview */}
        {parsedPreview && (
          <div className="p-6 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/40 dark:to-emerald-950/40 border-2 border-green-300 dark:border-green-700 mb-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
                <p className="font-bold text-lg text-green-900 dark:text-green-100">
                  AI Understood Your Workout Preferences
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setParsedPreview(null)}
                className="h-8 text-xs hover:bg-green-100 dark:hover:bg-green-900"
              >
                Clear
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Goal */}
              <div className="space-y-2 p-4 rounded-lg bg-white/60 dark:bg-gray-900/40 border border-green-200 dark:border-green-800">
                <p className="text-xs font-semibold text-green-700 dark:text-green-300 uppercase tracking-wide">
                  Goal
                </p>
                <div className="flex items-center gap-2">
                  {React.createElement(
                    goalLabels[parsedPreview.goal]?.icon || Dumbbell,
                    {
                      className: `h-5 w-5 ${
                        goalLabels[parsedPreview.goal]?.color || "text-gray-500"
                      }`,
                    }
                  )}
                  <p className="font-bold text-green-900 dark:text-green-100">
                    {goalLabels[parsedPreview.goal]?.label ||
                      parsedPreview.goal.replace("_", " ")}
                  </p>
                </div>
              </div>

              {/* Experience */}
              <div className="space-y-2 p-4 rounded-lg bg-white/60 dark:bg-gray-900/40 border border-green-200 dark:border-green-800">
                <p className="text-xs font-semibold text-green-700 dark:text-green-300 uppercase tracking-wide">
                  Experience Level
                </p>
                <p className="font-bold text-green-900 dark:text-green-100 capitalize">
                  {parsedPreview.experience_level}
                </p>
              </div>

              {/* Training Schedule */}
              <div className="space-y-2 p-4 rounded-lg bg-white/60 dark:bg-gray-900/40 border border-green-200 dark:border-green-800">
                <p className="text-xs font-semibold text-green-700 dark:text-green-300 uppercase tracking-wide">
                  Training Schedule
                </p>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-green-600" />
                  <p className="font-bold text-green-900 dark:text-green-100">
                    {parsedPreview.days_per_week} days/week
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-green-600" />
                  <p className="font-bold text-green-900 dark:text-green-100">
                    {parsedPreview.session_length_mins} mins/session
                  </p>
                </div>
              </div>
            </div>

            {/* Equipment & Constraints */}
            <div className="mt-4 p-4 rounded-lg bg-white/60 dark:bg-gray-900/40 border border-green-200 dark:border-green-800">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {parsedPreview.equipment && (
                  <div>
                    <p className="text-xs font-semibold text-green-700 dark:text-green-300 uppercase tracking-wide mb-2">
                      Equipment
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {parsedPreview.equipment.map((eq) => (
                        <Badge
                          key={eq}
                          variant="secondary"
                          className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        >
                          {eq}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {parsedPreview.injuries && parsedPreview.injuries.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-red-700 dark:text-red-300 uppercase tracking-wide mb-2">
                      Injuries / Limitations
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {parsedPreview.injuries.map((inj) => (
                        <Badge
                          key={inj}
                          variant="destructive"
                          className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                        >
                          <AlertCircle className="h-3 w-3 mr-1" />
                          {inj}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Generate Plan Button */}
        <Button
          onClick={handleGeneratePlan}
          disabled={generating}
          className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-xl text-lg py-6"
          size="lg"
        >
          {generating ? (
            <>
              <Loader2 className="mr-2 h-6 w-6 animate-spin" />
              Generating Your Workout Plan...
            </>
          ) : (
            <>
              <Dumbbell className="mr-2 h-6 w-6" />
              Generate My Workout Plan
            </>
          )}
        </Button>

        {/* Weekly Plan View */}
        {weeklyPlan && (
          <div className="mt-10 space-y-6">
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Your Weekly Schedule
              </h2>
              <p className="text-muted-foreground">
                Follow this schedule to achieve your fitness goals safely and
                effectively.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {Object.entries(weeklyPlan.weekly_plan).map(([day, session]) => (
                <div
                  key={day}
                  className={`glass-card p-6 border-2 transition-all hover:shadow-xl ${
                    session === "rest"
                      ? "border-gray-300 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30"
                      : "border-purple-200 dark:border-purple-800 hover:border-purple-400"
                  }`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-lg capitalize">{formatDay(day)}</h3>
                    {session === "rest" ? (
                      <Badge variant="secondary" className="bg-gray-200 text-gray-700">
                        Rest Day
                      </Badge>
                    ) : (
                      <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                        Training
                      </Badge>
                    )}
                  </div>

                  {session === "rest" ? (
                    <p className="text-sm text-muted-foreground italic">
                      Rest / light movement (easy walking, stretching). Recovery is
                      essential for progress.
                    </p>
                  ) : Array.isArray(session) ? (
                    <ul className="space-y-3">
                      {session.map((item: any, idx: number) => {
                        if (item.type === "warmup") {
                          return (
                            <li
                              key={idx}
                              className="text-xs p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded border border-yellow-200 dark:border-yellow-800"
                            >
                              <span className="font-semibold text-yellow-700 dark:text-yellow-300">
                                Warm-up:
                              </span>{" "}
                              {item.description}
                            </li>
                          );
                        }
                        if (item.type === "cooldown") {
                          return (
                            <li
                              key={idx}
                              className="text-xs p-2 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800"
                            >
                              <span className="font-semibold text-blue-700 dark:text-blue-300">
                                Cool-down:
                              </span>{" "}
                              {item.description}
                            </li>
                          );
                        }
                        if (item.type === "cardio") {
                          return (
                            <li
                              key={idx}
                              className="text-sm p-3 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800"
                            >
                              <div className="flex items-start gap-2">
                                <Heart className="h-4 w-4 text-green-600 mt-0.5" />
                                <div>
                                  <p className="font-semibold text-green-700 dark:text-green-300">
                                    Cardio: {item.mode}
                                  </p>
                                  <p className="text-xs text-green-600 dark:text-green-400">
                                    {item.minutes} mins • {item.intensity} intensity
                                  </p>
                                </div>
                              </div>
                            </li>
                          );
                        }
                        return (
                          <li key={idx} className="text-sm">
                            <div className="flex items-start gap-2">
                              <Dumbbell className="h-4 w-4 text-purple-600 mt-0.5" />
                              <div>
                                <p className="font-semibold">{item.name}</p>
                                <p className="text-xs text-muted-foreground">
                                  {item.sets} sets × {item.reps} reps
                                </p>
                              </div>
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      No session details.
                    </p>
                  )}
                </div>
              ))}
            </div>

            {/* Guidelines */}
            {weeklyPlan.guidelines && (
              <div className="glass-card p-6 border-2 border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-950/30">
                <h3 className="font-bold text-lg mb-4 flex items-center gap-2 text-blue-900 dark:text-blue-100">
                  <AlertCircle className="h-5 w-5 text-blue-600" />
                  Important Guidelines
                </h3>
                <ul className="space-y-2">
                  {weeklyPlan.guidelines.map((guideline, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-blue-800 dark:text-blue-200 flex items-start gap-2"
                    >
                      <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span>{guideline}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkoutPlan;
