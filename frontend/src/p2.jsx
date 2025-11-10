import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import {
  FaCalendarAlt,
  FaDollarSign,
  FaBullseye,
  FaBalanceScale,
} from "react-icons/fa";
import "./p2.css";

// ✅ Reusable summary card component
const SummaryCard = ({ icon, title, value, valueColor }) => {
  return (
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
};

const P2 = () => {
  const { state } = useLocation();
  const formData = state?.formData;

  // --- AI Insight State ---
  const [agentOutput, setAgentOutput] = useState(null);

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

      // --- Calculate Years to Retirement ---
      const currentAge = parseInt(personal_info.current_age || 0);
      const retireAge = parseInt(retirement_info.desired_retirement_age || 0);
      const yearsToRetirement =
        retireAge > currentAge ? retireAge - currentAge : 0;

      // --- Calculate Current Assets ---
      const s = financial_info.assets.savings;
      const currentAssets =
        parseFloat(s.epf || 0) +
        parseFloat(s.ppf || 0) +
        parseFloat(s.nps || 0) +
        parseFloat(s.bank_savings || 0) +
        parseFloat(financial_info.assets.total_investments || 0);

      // --- Retirement Goal (Desired monthly expenses) ---
      const retirementGoal = parseFloat(
        retirement_info.desired_retirement_expenses_inr || 0
      );

      // --- Risk Tolerance ---
      const riskToleranceScore = parseInt(
        retirement_info.risk_tolerance_score || 5
      );
      let riskTolerance = "Moderate";
      if (riskToleranceScore <= 3) riskTolerance = "Conservative";
      else if (riskToleranceScore <= 7) riskTolerance = "Balanced";
      else riskTolerance = "Aggressive";

      // --- Projected Savings (simple linear projection) ---
      const annualIncome = parseFloat(financial_info.income.annual || 0);
      const annualSavingsRate = parseFloat(
        retirement_info.annual_savings_rate_percent || 0
      );
      const monthlyContribution = (annualIncome * annualSavingsRate) / 100 / 12;

      // assume 6% annual return for projection
      const r = 0.06; // interest rate
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

  // --- Fetch AI Insight from Backend ---
  useEffect(() => {
    if (formData) {
      setAgentOutput(null); // reset before fetch
      fetch("http://127.0.0.1:5000/ai_insights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })
        .then((res) => {
          if (!res.ok) throw new Error("Network response was not ok");
          return res.json();
        })
        .then((data) => {
          setAgentOutput(
            data.message || data.output || "No insights available."
          );
        })
        .catch((err) => {
          console.error("Error fetching AI insights:", err);
          setAgentOutput("Failed to fetch insights. Please try again later.");
        });
    }
  }, [formData]);

  const recommendations = [
    "Increase your monthly savings rate to close the gap between your goal and projections.",
    "Diversify investments across equity, debt, and gold for balanced returns.",
    "Review your asset allocation yearly to align with your risk profile.",
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

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
        <h2>AI Agent Insights</h2>
        <p className="card-subtitle">
          Personalized analysis based on your financial data
        </p>
        <div className="agent-response-box">
          {agentOutput ? agentOutput : "Please wait..."}
        </div>
      </div>

      {/* Details Grid */}
      <div className="details-grid">
        {/* Projected Savings Card */}
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

        {/* Recommendations Card */}
        <div className="card recommendations">
          <h2>Recommendations</h2>
          <p className="card-subtitle">
            Steps to improve your retirement readiness
          </p>
          <ol className="recommendations-list">
            {recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ol>
        </div>
      </div>

      {/* Call to Action */}
      <footer className="cta-section">
        <h3>Ready to take action?</h3>
        <p>Schedule a consultation with one of our retirement experts.</p>
      </footer>
    </div>
  );
};

export default P2;
