import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navigation from "./components/Navigation";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import Profile from "./pages/Profile";
import UpdateData from "./pages/UpdateData";
import SymptomChecker from "./pages/SymptomChecker";
import DietPlan from "./pages/DietPlan";
import Analytics from "./pages/Analytics";
import Explorer from "./pages/Explorer";
import Dashboard from "./pages/Dashboard";
import Support from "./pages/Support";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

/*------- New Import for AI Chatbot Page -------*/
import AIChatbot from './pages/AIChatbot';


const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div className="flex flex-col min-h-screen">
          <Navigation />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/auth" element={<Auth />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/update-data" element={<UpdateData />} />
              <Route path="/symptom-checker" element={<SymptomChecker />} />
              <Route path="/diet-plan" element={<DietPlan />} />
              /*------- New Route for AI Chatbot Page -------*/
              <Route path="/ai-chatbot" element={<AIChatbot />} />

              <Route path="/analytics" element={<Analytics />} />
              <Route path="/explorer" element={<Explorer />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/support" element={<Support />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
