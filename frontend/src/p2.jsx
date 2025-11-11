import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import ReactMarkdown from "react-markdown"; // ✅ for markdown rendering
import {
  FaCalendarAlt,
  FaDollarSign,
  FaBullseye,
  FaBalanceScale,
} from "react-icons/fa";
import "./p2.css";

const SummaryCard = ({ icon, title, value, valueColor }) => (
  <div className="card summary-card">
    <div className="summary-card-icon">{icon}</div>
    <div className="summary-card-info">
      <div className="summary-card-title">{title}</div>
      <div className="summary-card-value" style={{ color: valueColor }}>
        {value}
      </div>
    </div>
  </div>
);

const P2 = () => {
  const { state } = useLocation();
  const formData = state?.formData;
  const aiPlan = state?.aiPlan;

  const [agentOutput, setAgentOutput] = useState(""); // store progressively typed text
  const [isLoading, setIsLoading] = useState(true); // loader control

  const [overviewData, setOverviewData] = useState({
    yearsToRetirement: 0,
    currentAssets: 0,
    retirementGoal: 0,
    riskTolerance: "N/A",
  });

  const [projectedSavings, setProjectedSavings] = useState({
    currentAssets: 0,
    monthlyContribution: 0,
    projectedAtRetirement: 0,
    savingsGap: 0,
  });

  // --- Calculate summary data ---
  useEffect(() => {
    if (formData) {
      const { personal_info, financial_info, retirement_info } = formData;
      const currentAge = parseInt(personal_info.current_age || 0);
      const retireAge = parseInt(retirement_info.desired_retirement_age || 0);
      const yearsToRetirement =
        retireAge > currentAge ? retireAge - currentAge : 0;

      const s = financial_info.assets.savings;
      const currentAssets =
        parseFloat(s.epf || 0) +
        parseFloat(s.ppf || 0) +
        parseFloat(s.nps || 0) +
        parseFloat(s.bank_savings || 0) +
        parseFloat(financial_info.assets.total_investments || 0);

      const retirementGoal = parseFloat(
        retirement_info.desired_retirement_expenses_inr || 0
      );

      const riskToleranceScore = parseInt(
        retirement_info.risk_tolerance_score || 5
      );
      let riskTolerance = "Moderate";
      if (riskToleranceScore <= 3) riskTolerance = "Conservative";
      else if (riskToleranceScore <= 7) riskTolerance = "Balanced";
      else riskTolerance = "Aggressive";

      const annualIncome = parseFloat(financial_info.income.annual || 0);
      const annualSavingsRate = parseFloat(
        retirement_info.annual_savings_rate_percent || 0
      );
      const monthlyContribution = (annualIncome * annualSavingsRate) / 100 / 12;

      const r = 0.06;
      const n = yearsToRetirement;
      let projectedAtRetirement = currentAssets;
      for (let i = 0; i < n; i++) {
        projectedAtRetirement =
          (projectedAtRetirement + monthlyContribution * 12) * (1 + r);
      }

      const savingsGap = retirementGoal * 12 * (n / 2) - projectedAtRetirement;

      setOverviewData({
        yearsToRetirement,
        currentAssets,
        retirementGoal,
        riskTolerance,
      });

      setProjectedSavings({
        currentAssets,
        monthlyContribution,
        projectedAtRetirement,
        savingsGap,
      });
    }
  }, [formData]);

  // --- Typing effect for plan display ---
  const simulateTyping = (text) => {
    setAgentOutput(""); // reset previous text
    setIsLoading(false);
    let i = 0;
  
    const typeNext = () => {
      // progressively show text
      setAgentOutput(text.substring(0, i));
  
      if (i < text.length) {
        i++;
  
        // Slow down slightly at punctuation for realism
        const currentChar = text.charAt(i);
        let delay = 12; // base typing speed
        if ([",", ";"].includes(currentChar)) delay = 60;
        if ([".", "!", "?"].includes(currentChar)) delay = 120;
  
        setTimeout(typeNext, delay);
      }
    };
  
    typeNext();
  };

  // --- Display AI plan (from backend or prop) ---
  useEffect(() => {
    if (aiPlan) {
      // ✅ Already available from previous page
      setIsLoading(true);
      setTimeout(() => simulateTyping(aiPlan), 700); // delay to show loader briefly
      return;
    }

    // fallback: fetch again if not passed
    if (formData) {
      setIsLoading(true);
      fetch("http://127.0.0.1:5000/trial", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })
        .then((res) => res.json())
        .then((data) => {
          const planText = data.plan || "No insights available.";
          simulateTyping(planText);
        })
        .catch((err) => {
          console.error("Error fetching AI insights:", err);
          setAgentOutput("Failed to fetch insights. Please try again later.");
          setIsLoading(false);
        });
    }
  }, [formData, aiPlan]);

  const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);

  if (!formData) {
    return (
      <div className="retirement-overview-container">
        <h2>No data found.</h2>
        <p>Please complete the retirement form first.</p>
      </div>
    );
  }

  return (
    <div className="retirement-overview-container">
      <header>
        <h1>Your Retirement Plan Overview</h1>
        <p>
          Based on your responses, here's a personalized snapshot of your
          retirement readiness.
        </p>
      </header>

      {/* Top Summary Grid */}
      <div className="summary-grid">
        <SummaryCard
          icon={<FaCalendarAlt />}
          title="Years to Retirement"
          value={overviewData.yearsToRetirement}
          valueColor="#007bff"
        />
        <SummaryCard
          icon={<FaDollarSign />}
          title="Current Assets"
          value={formatCurrency(overviewData.currentAssets)}
          valueColor="#28a745"
        />
        <SummaryCard
          icon={<FaBullseye />}
          title="Retirement Goal"
          value={formatCurrency(overviewData.retirementGoal)}
          valueColor="#007bff"
        />
        <SummaryCard
          icon={<FaBalanceScale />}
          title="Risk Tolerance"
          value={overviewData.riskTolerance}
          valueColor="#17a2b8"
        />
      </div>

      {/* ✅ AI Agent Output Box */}
      <div className="card agent-output">
        <h2>Your Personalised Retirement Plan</h2>
        <p className="card-subtitle">
          Personalized plan based on your financial data
        </p>

        <div className="agent-response-box">
          {isLoading ? (
            <div className="loading-spinner"></div>
          ) : (
            <ReactMarkdown>{agentOutput}</ReactMarkdown>
          )}
        </div>
      </div>

      {/* Details Grid */}
      <div className="details-grid">
        <div className="card projected-savings">
          <h2>Projected Savings</h2>
          <p className="card-subtitle">
            Based on your current savings rate and timeline
          </p>
          <div className="savings-list">
            <div className="savings-item">
              <span>Current Assets</span>
              <span>{formatCurrency(projectedSavings.currentAssets)}</span>
            </div>
            <div className="savings-item">
              <span>Monthly Contribution</span>
              <span>
                {formatCurrency(projectedSavings.monthlyContribution)}
              </span>
            </div>
            <div className="savings-item">
              <span>Projected at Retirement</span>
              <span>
                {formatCurrency(projectedSavings.projectedAtRetirement)}
              </span>
            </div>
          </div>
          <div className="savings-gap">
            <span>Savings Gap</span>
            <span
              style={{
                color: projectedSavings.savingsGap > 0 ? "#dc3545" : "#28a745",
              }}
            >
              {formatCurrency(projectedSavings.savingsGap)}
            </span>
          </div>
        </div>
      </div>

      <footer className="cta-section">
        <h3>Ready to take action?</h3>
        <p>Schedule a consultation with one of our retirement experts.</p>
      </footer>
    </div>
  );
};

export default P2;
