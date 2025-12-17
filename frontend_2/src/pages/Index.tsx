import { useState } from "react";
import LandingPage from "@/components/LandingPage";
import QuickSetupForm from "@/components/QuickSetupForm";
import ChatPage from "@/components/ChatPage";
import AssessmentForm from "@/components/AssessmentForm";
import ResultsPage from "@/components/ResultsPage";

const Index = () => {
  const [currentView, setCurrentView] = useState("landing");
  const [userData, setUserData] = useState(null);
  const [assessmentResults, setAssessmentResults] = useState(null);

  const renderView = () => {
    switch (currentView) {
      case "landing":
        return <LandingPage onGetStarted={() => setCurrentView("setup")} />;
      case "setup":
        return (
          <QuickSetupForm
            onComplete={(data) => {
              setUserData(data);
              localStorage.setItem("quickSetupData", JSON.stringify(data));
              setCurrentView("chat");
            }}
          />
        );
      case "chat":
        return (
          <ChatPage
            userData={userData}
            onStartAssessment={() => setCurrentView("assessment")}
          />
        );
      case "assessment":
        return (
          <AssessmentForm
            userData={userData}
            onComplete={(results) => {
              setAssessmentResults(results);
              setCurrentView("results");
            }}
          />
        );
      case "results":
        return (
          <ResultsPage
            results={assessmentResults}
            onBackToHome={() => setCurrentView("landing")}
          />
        );
      default:
        return <LandingPage onGetStarted={() => setCurrentView("setup")} />;
    }
  };

  return <div className="min-h-screen bg-background">{renderView()}</div>;
};

export default Index;
