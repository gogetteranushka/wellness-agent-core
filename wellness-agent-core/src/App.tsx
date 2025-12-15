import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navigation from "./components/Navigation";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import Profile from "./pages/Profile";
import UpdateData from "./pages/UpdateData";
import SymptomChecker from "./pages/SymptomChecker";
import DietPlan from "./pages/DietPlan";
import NutritionPredictor from "./pages/NutritionPredictor";
import Analytics from "./pages/Analytics";
import Explorer from "./pages/Explorer";
import Support from "./pages/Support";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import { useEffect, useState } from 'react';
import { supabase } from '../supabaseClient';
import Onboarding from "./pages/Onboarding";
import UserDashboard from './pages/Dashboard';


/*------- New Import for AI Chatbot Page -------*/
import AIChatbot from './pages/AIChatbot';




const queryClient = new QueryClient();

function App() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize auth - DO NOT sign out automatically
    const initAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setSession(session);
      setLoading(false);
    };

    initAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    // Cleanup subscription on unmount
    return () => {
      subscription.unsubscribe();
    };
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse">
          <p className="text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <div className="min-h-screen flex flex-col">
            {session && <Navigation />}
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Home />} />
                {/* Redirect to profile after login instead of symptom-checker */}
                <Route path="/auth" element={!session ? <Auth /> : <Navigate to="/profile" />} />
                <Route path="/profile" element={session ? <Profile /> : <Navigate to="/auth" />} />
                <Route path="/update-data" element={session ? <UpdateData /> : <Navigate to="/auth" />} />
                <Route path="/symptom-checker" element={session ? <SymptomChecker /> : <Navigate to="/auth" />} />
                <Route path="/diet-plan" element={session ? <DietPlan /> : <Navigate to="/auth" />} />
                <Route path="/nutrition-predictor" element={session ? <NutritionPredictor /> : <Navigate to="/auth" />} />
                <Route path="/analytics" element={session ? <Analytics /> : <Navigate to="/auth" />} />
                <Route path="/explorer" element={session ? <Explorer /> : <Navigate to="/auth" />} />
                <Route path="/support" element={session ? <Support /> : <Navigate to="/auth" />} />
                <Route path="/settings" element={session ? <Settings /> : <Navigate to="/auth" />} />
                <Route path="/onboarding" element={session ? <Onboarding /> : <Navigate to="/auth" />} />
                <Route path="/ai-chatbot" element={session ? <AIChatbot /> : <Navigate to="/auth" />} />
                <Route path="/dashboard" element={session ? <UserDashboard /> : <Navigate to="/auth" />} />
                <Route path="*" element={<NotFound />} />
                <Route
                  path="/profile"
                  element={session ? <Profile /> : <Navigate to="/auth" />}
                />

              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
