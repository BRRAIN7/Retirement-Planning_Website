import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import "./App.css";
import {
  FaClipboardList,
  FaChartLine,
  FaShieldAlt,
  FaBullseye,
} from "react-icons/fa";

// ✅ Use capital letter for component import
import P1 from "./p1";
import P2 from "./p2";

// ✅ Moved navigation logic into a separate Home component
function HomePage() {
  const navigate = useNavigate(); // used correctly inside Router

  const handleStart = () => {
    navigate("/p1"); // navigate to new page
  };

  return (
    <div className="planner-container">
      {/* --- Hero Section --- */}
      <main className="hero-section">
        <h2>Plan Your Perfect</h2>
        <h1 className="hero-title-highlight">Retirement Journey</h1>
        <p className="hero-subtitle">
          Take our comprehensive assessment to understand your retirement
          readiness and get personalized recommendations for your financial
          future.
        </p>

        {/* ✅ Added onClick handler */}
        <button className="hero-cta-button" onClick={handleStart}>
          Start Your Assessment
        </button>
      </main>

      {/* --- Features Section --- */}
      <section className="features-section">
        <div className="feature-card">
          <div className="feature-icon-wrapper icon-analysis">
            <FaClipboardList className="feature-icon" />
          </div>
          <h3>Comprehensive Analysis</h3>
          <p>
            Detailed assessment of your financial situation and retirement
            goals.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper icon-projections">
            <FaChartLine className="feature-icon" />
          </div>
          <h3>Personalized Projections</h3>
          <p>
            See how your current savings will grow over time to meet your goals.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper icon-risk">
            <FaShieldAlt className="feature-icon" />
          </div>
          <h3>Risk Assessment</h3>
          <p>
            Understand your risk tolerance and get matched investment
            strategies.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper icon-insights">
            <FaBullseye className="feature-icon" />
          </div>
          <h3>Actionable Insights</h3>
          <p>Get clear recommendations to improve your retirement readiness.</p>
        </div>
      </section>
    </div>
  );
}

// ✅ App now wraps everything with Router and defines routes
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} /> {/* home route */}
        <Route path="/p1" element={<P1 />} /> {/* your new page */}
        <Route path="/p2" element={<P2 />} /> {/* ✅ Add this route */}
      </Routes>
    </Router>
  );
}

export default App;
