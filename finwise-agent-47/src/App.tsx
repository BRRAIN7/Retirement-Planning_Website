import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { useState } from "react";

// Pages
import LandingPage from "./components/LandingPage";
import QuickSetupForm from "./components/QuickSetupForm";
import ChatPage from "./components/ChatPage";
import AssessmentForm from "./components/AssessmentForm";
import ResultsPage from "./components/ResultsPage";
import AuthPage from "./components/AuthPage";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";

const queryClient = new QueryClient();

const AppRoutes = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState<any>(null);
  const [assessmentResults, setAssessmentResults] = useState<any>(null);

  return (
    <Routes>
      {/* 🏠 Landing Page */}
      <Route
        path="/"
        element={<LandingPage onGetStarted={() => navigate("/auth")} />}
      />

      {/* 🔐 Auth */}
      <Route path="/auth" element={<AuthPage />} />

      {/* ⚙️ Setup (only after signup) */}
      <Route
        path="/setup"
        element={
          <ProtectedRoute>
            <QuickSetupForm
              onComplete={(data) => {
                setUserData(data);
                navigate("/chat"); // ✅ redirect to chat after setup
              }}
            />
          </ProtectedRoute>
        }
      />

      {/* 💬 Chat (main AI page) */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage
              userData={userData}
              onStartAssessment={() => navigate("/assessment")}
            />
          </ProtectedRoute>
        }
      />

      {/* 📈 Assessment */}
      <Route
        path="/assessment"
        element={
          <ProtectedRoute>
            <AssessmentForm
              onComplete={(results) => {
                setAssessmentResults(results);
                navigate("/results");
              }}
            />
          </ProtectedRoute>
        }
      />


      {/* 📊 Results */}
      <Route
        path="/results"
        element={
          <ProtectedRoute>
            <ResultsPage
              results={assessmentResults}
              onBackToHome={() => navigate("/chat")}
            />
          </ProtectedRoute>
        }
      />

      {/* 🚫 Not Found */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
