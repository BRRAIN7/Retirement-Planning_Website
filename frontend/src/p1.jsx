import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
// Main App Component
const P1 = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    personal_info: {
      name: "",
      current_age: "",
      gender: "",
      marital_status: "",
      number_of_children: "",
    },
    financial_info: {
      income: {
        annual: "",
      },
      expenses: {
        monthly_total: "",
        components: {
          loan_emis: "",
          investment_sips: "",
          misc: "",
        },
      },
      assets: {
        savings: {
          epf: "",
          ppf: "",
          nps: "",
          bank_savings: "",
        },
        total_investments: "",
        portfolio_breakdown_percent: {
          equity: "",
          mutual_funds: "",
          gold: "",
          crypto: "",
          other: "",
        },
        emergency_fund: "",
      },
      liabilities: {
        total_debt: "",
        monthly_debt_contribution: "",
      },
    },
    goals: {
      short_term: [],
      medium_term: [],
      long_term: [],
    },
    retirement_info: {
      desired_retirement_age: "",
      retirement_lifestyle_description: "",
      desired_retirement_expenses_inr: "",
      risk_tolerance_score: 5,
      investment_preferences: "",
      annual_savings_rate_percent: "",
    },
  });

  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);

  // Handles changes in nested state properties
  const handleNestedChange = (path) => (e) => {
    const { value, type, checked } = e.target;
    const val = type === "checkbox" ? checked : value;

    setFormData((prev) => {
      const newState = JSON.parse(JSON.stringify(prev)); // Deep copy
      let current = newState;
      for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]];
      }
      current[path[path.length - 1]] = val;
      return newState;
    });
  };

  // --- Goal Handlers ---
  const addGoal = (goalType) => {
    const newGoal = { name: "", target_amount: "" };
    setFormData((prev) => ({
      ...prev,
      goals: {
        ...prev.goals,
        [goalType]: [...prev.goals[goalType], newGoal],
      },
    }));
  };

  const removeGoal = (goalType, index) => {
    setFormData((prev) => ({
      ...prev,
      goals: {
        ...prev.goals,
        [goalType]: prev.goals[goalType].filter((_, i) => i !== index),
      },
    }));
  };

  const handleGoalChange = (goalType, index, e) => {
    const { name, value } = e.target;
    const updatedGoals = [...formData.goals[goalType]];
    updatedGoals[index][name] = value;
    setFormData((prev) => ({
      ...prev,
      goals: { ...prev.goals, [goalType]: updatedGoals },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    fetch("http://127.0.0.1:5000/trial", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData), // formData should match the backend's expected keys
    })
      .then((response) => {
        if (response.status === 204) {
          console.log("Data sent successfully");
          navigate("/p2", { state: { formData } }); 
        } else {
          console.error("Unexpected status:", response.status);
        }
      })
      .catch((err) => console.error("Error:", err));
  };

  // Render current step based on the 'step' state
  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <Step1
            nextStep={nextStep}
            handleChange={handleNestedChange}
            data={formData.personal_info}
          />
        );
      case 2:
        return (
          <Step2
            nextStep={nextStep}
            prevStep={prevStep}
            handleChange={handleNestedChange}
            data={formData.financial_info}
          />
        );
      case 3:
        return (
          <Step3
            nextStep={nextStep}
            prevStep={prevStep}
            handleChange={handleNestedChange}
            data={formData.financial_info.assets}
          />
        );
      case 4:
        return (
          <GoalStep
            nextStep={nextStep}
            prevStep={prevStep}
            handleGoalChange={handleGoalChange}
            addGoal={addGoal}
            removeGoal={removeGoal}
            goals={formData.goals.short_term}
            goalType="short_term"
            title="Short-Term Goals"
          />
        );
      case 5:
        return (
          <GoalStep
            nextStep={nextStep}
            prevStep={prevStep}
            handleGoalChange={handleGoalChange}
            addGoal={addGoal}
            removeGoal={removeGoal}
            goals={formData.goals.medium_term}
            goalType="medium_term"
            title="Medium-Term Goals"
          />
        );
      case 6:
        return (
          <GoalStep
            nextStep={nextStep}
            prevStep={prevStep}
            handleGoalChange={handleGoalChange}
            addGoal={addGoal}
            removeGoal={removeGoal}
            goals={formData.goals.long_term}
            goalType="long_term"
            title="Long-Term Goals"
          />
        );
      case 7:
        return (
          <Step5
            nextStep={nextStep}
            prevStep={prevStep}
            handleChange={handleNestedChange}
            data={formData.retirement_info}
          />
        );
      case 8:
        return (
          <Summary
            prevStep={prevStep}
            formData={formData}
            handleSubmit={handleSubmit}
          />
        );
      case 9:
        return <Success />;
      default:
        return (
          <Step1
            nextStep={nextStep}
            handleChange={handleNestedChange}
            data={formData.personal_info}
          />
        );
    }
  };

  const totalSteps = 9;

  return (
    <div className="bg-slate-100 min-h-screen flex flex-col items-center justify-center font-sans p-4">
      <div className="w-full max-w-2xl">
        <h1 className="text-3xl font-bold text-center text-slate-700 mb-2">
          Retirement Planner
        </h1>
        <p className="text-center text-slate-500 mb-6">
          Let's build your financial future, one step at a time.
        </p>

        {step < totalSteps && (
          <div className="flex items-center justify-between mb-8 px-4">
            {[...Array(totalSteps - 1)].map((_, i) => {
              const stepNum = i + 1;
              const isCompleted = stepNum < step;
              const isActive = stepNum === step;
              return (
                <div key={i} className="flex-1 flex items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors duration-500 ${
                      isCompleted
                        ? "bg-indigo-600 border-indigo-600 text-white"
                        : isActive
                        ? "border-indigo-600 text-indigo-600"
                        : "border-slate-300 text-slate-500"
                    }`}
                  >
                    {stepNum}
                  </div>
                  {i < totalSteps - 2 && (
                    <div
                      className={`flex-1 h-1 transition-all duration-500 ${
                        isCompleted ? "bg-indigo-600" : "bg-slate-300"
                      }`}
                    ></div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-xl p-8">{renderStep()}</div>
      </div>
    </div>
  );
};

// --- Step Components ---

const Step1 = ({ nextStep, handleChange, data }) => (
  <div>
    <h2 className="text-2xl font-semibold mb-6 text-slate-800">
      Personal Information
    </h2>
    <div className="space-y-4">
      <InputField
        label="Your Name"
        name="name"
        value={data.name}
        onChange={handleChange(["personal_info", "name"])}
      />
      <InputField
        label="Current Age"
        name="current_age"
        type="number"
        value={data.current_age}
        onChange={handleChange(["personal_info", "current_age"])}
      />
      <SelectField
        label="Gender"
        name="gender"
        value={data.gender}
        onChange={handleChange(["personal_info", "gender"])}
        options={["Male", "Female", "Other"]}
      />
      <SelectField
        label="Marital Status"
        name="marital_status"
        value={data.marital_status}
        onChange={handleChange(["personal_info", "marital_status"])}
        options={["Single", "Married", "Divorced", "Widowed"]}
      />
      <InputField
        label="Number of Children"
        name="number_of_children"
        type="number"
        value={data.number_of_children}
        onChange={handleChange(["personal_info", "number_of_children"])}
      />
    </div>
    <button
      onClick={nextStep}
      className="mt-8 w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition"
    >
      Next
    </button>
  </div>
);

const Step2 = ({ nextStep, prevStep, handleChange, data }) => (
  <div>
    <h2 className="text-2xl font-semibold mb-6 text-slate-800">
      Income & Expenses
    </h2>
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-slate-600 border-b pb-2">
        Income
      </h3>
      <InputField
        label="Annual Income (INR)"
        name="annual"
        type="number"
        value={data.income.annual}
        onChange={handleChange(["financial_info", "income", "annual"])}
      />

      <h3 className="text-lg font-medium text-slate-600 border-b pb-2 mt-6">
        Expenses & Liabilities
      </h3>
      <InputField
        label="Total Monthly Expenses (INR)"
        name="monthly_total"
        type="number"
        value={data.expenses.monthly_total}
        onChange={handleChange(["financial_info", "expenses", "monthly_total"])}
      />
      <InputField
        label="Loan EMIs (INR)"
        name="loan_emis"
        type="number"
        value={data.expenses.components.loan_emis}
        onChange={handleChange([
          "financial_info",
          "expenses",
          "components",
          "loan_emis",
        ])}
      />
      <InputField
        label="Investment SIPs (INR)"
        name="investment_sips"
        type="number"
        value={data.expenses.components.investment_sips}
        onChange={handleChange([
          "financial_info",
          "expenses",
          "components",
          "investment_sips",
        ])}
      />
      <InputField
        label="Miscellaneous Expenses (INR)"
        name="misc"
        type="number"
        value={data.expenses.components.misc}
        onChange={handleChange([
          "financial_info",
          "expenses",
          "components",
          "misc",
        ])}
      />
      <InputField
        label="Total Debt (INR)"
        name="total_debt"
        type="number"
        value={data.liabilities.total_debt}
        onChange={handleChange(["financial_info", "liabilities", "total_debt"])}
      />
      <InputField
        label="Monthly Debt Contribution (INR)"
        name="monthly_debt_contribution"
        type="number"
        value={data.liabilities.monthly_debt_contribution}
        onChange={handleChange([
          "financial_info",
          "liabilities",
          "monthly_debt_contribution",
        ])}
      />
    </div>
    <div className="flex justify-between mt-8">
      <button
        onClick={prevStep}
        className="bg-slate-300 text-slate-800 py-2 px-4 rounded-md hover:bg-slate-400 transition"
      >
        Back
      </button>
      <button
        onClick={nextStep}
        className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition"
      >
        Next
      </button>
    </div>
  </div>
);

const Step3 = ({ nextStep, prevStep, handleChange, data }) => (
  <div>
    <h2 className="text-2xl font-semibold mb-6 text-slate-800">
      Assets & Investments
    </h2>
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-slate-600 border-b pb-2">
        Savings
      </h3>
      <InputField
        label="EPF (INR)"
        name="epf"
        type="number"
        value={data.savings.epf}
        onChange={handleChange(["financial_info", "assets", "savings", "epf"])}
      />
      <InputField
        label="PPF (INR)"
        name="ppf"
        type="number"
        value={data.savings.ppf}
        onChange={handleChange(["financial_info", "assets", "savings", "ppf"])}
      />
      <InputField
        label="NPS (INR)"
        name="nps"
        type="number"
        value={data.savings.nps}
        onChange={handleChange(["financial_info", "assets", "savings", "nps"])}
      />
      <InputField
        label="Bank Savings (INR)"
        name="bank_savings"
        type="number"
        value={data.savings.bank_savings}
        onChange={handleChange([
          "financial_info",
          "assets",
          "savings",
          "bank_savings",
        ])}
      />
      <InputField
        label="Emergency Fund (INR)"
        name="emergency_fund"
        type="number"
        value={data.emergency_fund}
        onChange={handleChange(["financial_info", "assets", "emergency_fund"])}
      />

      <h3 className="text-lg font-medium text-slate-600 border-b pb-2 mt-6">
        Investments
      </h3>
      <InputField
        label="Total Investments (INR)"
        name="total_investments"
        type="number"
        value={data.total_investments}
        onChange={handleChange([
          "financial_info",
          "assets",
          "total_investments",
        ])}
      />
      <p className="text-md font-medium text-slate-600 mt-4">
        Portfolio Breakdown (%)
      </p>
      <div className="grid grid-cols-2 gap-4">
        <InputField
          label="Equity"
          name="equity"
          type="number"
          value={data.portfolio_breakdown_percent.equity}
          onChange={handleChange([
            "financial_info",
            "assets",
            "portfolio_breakdown_percent",
            "equity",
          ])}
        />
        <InputField
          label="Mutual Funds"
          name="mutual_funds"
          type="number"
          value={data.portfolio_breakdown_percent.mutual_funds}
          onChange={handleChange([
            "financial_info",
            "assets",
            "portfolio_breakdown_percent",
            "mutual_funds",
          ])}
        />
        <InputField
          label="Gold"
          name="gold"
          type="number"
          value={data.portfolio_breakdown_percent.gold}
          onChange={handleChange([
            "financial_info",
            "assets",
            "portfolio_breakdown_percent",
            "gold",
          ])}
        />
        <InputField
          label="Crypto"
          name="crypto"
          type="number"
          value={data.portfolio_breakdown_percent.crypto}
          onChange={handleChange([
            "financial_info",
            "assets",
            "portfolio_breakdown_percent",
            "crypto",
          ])}
        />
        <InputField
          label="Other"
          name="other"
          type="number"
          value={data.portfolio_breakdown_percent.other}
          onChange={handleChange([
            "financial_info",
            "assets",
            "portfolio_breakdown_percent",
            "other",
          ])}
        />
      </div>
    </div>
    <div className="flex justify-between mt-8">
      <button
        onClick={prevStep}
        className="bg-slate-300 text-slate-800 py-2 px-4 rounded-md hover:bg-slate-400 transition"
      >
        Back
      </button>
      <button
        onClick={nextStep}
        className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition"
      >
        Next
      </button>
    </div>
  </div>
);

// Reusable component for each goal type step
const GoalStep = ({
  nextStep,
  prevStep,
  handleGoalChange,
  addGoal,
  removeGoal,
  goals,
  goalType,
  title,
}) => (
  <div>
    <h2 className="text-2xl font-semibold mb-6 text-slate-800">{title}</h2>
    {goals.map((goal, index) => (
      <div
        key={index}
        className="p-4 border rounded-md my-4 relative grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        <button
          onClick={() => removeGoal(goalType, index)}
          className="absolute top-2 right-2 text-slate-400 hover:text-red-500 text-2xl leading-none"
        >
          &times;
        </button>
        <InputField
          label="Goal Name"
          name="name"
          value={goal.name}
          onChange={(e) => handleGoalChange(goalType, index, e)}
        />
        <InputField
          label="Target Amount (INR)"
          name="target_amount"
          type="number"
          value={goal.target_amount}
          onChange={(e) => handleGoalChange(goalType, index, e)}
        />
      </div>
    ))}
    <button
      onClick={() => addGoal(goalType)}
      className="text-indigo-600 hover:text-indigo-800 transition"
    >
      + Add Goal
    </button>
    <div className="flex justify-between mt-8">
      <button
        onClick={prevStep}
        className="bg-slate-300 text-slate-800 py-2 px-4 rounded-md hover:bg-slate-400 transition"
      >
        Back
      </button>
      <button
        onClick={nextStep}
        className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition"
      >
        Next
      </button>
    </div>
  </div>
);

const Step5 = ({ nextStep, prevStep, handleChange, data }) => (
  <div>
    <h2 className="text-2xl font-semibold mb-6 text-slate-800">
      Retirement Preferences
    </h2>
    <div className="space-y-4">
      <InputField
        label="Desired Retirement Age"
        name="desired_retirement_age"
        type="number"
        value={data.desired_retirement_age}
        onChange={handleChange(["retirement_info", "desired_retirement_age"])}
      />
      <InputField
        label="Desired Monthly Expenses in Retirement (INR)"
        name="desired_retirement_expenses_inr"
        type="number"
        value={data.desired_retirement_expenses_inr}
        onChange={handleChange([
          "retirement_info",
          "desired_retirement_expenses_inr",
        ])}
      />
      <InputField
        label="Annual Savings Rate (%)"
        name="annual_savings_rate_percent"
        type="number"
        value={data.annual_savings_rate_percent}
        onChange={handleChange([
          "retirement_info",
          "annual_savings_rate_percent",
        ])}
      />
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Risk Tolerance ({data.risk_tolerance_score})
        </label>
        <input
          type="range"
          min="1"
          max="10"
          name="risk_tolerance_score"
          value={data.risk_tolerance_score}
          onChange={handleChange(["retirement_info", "risk_tolerance_score"])}
          className="w-full"
        />
      </div>
      <SelectField
        label="Investment Preferences"
        name="investment_preferences"
        value={data.investment_preferences}
        onChange={handleChange(["retirement_info", "investment_preferences"])}
        options={[
          "Saving",
          "Conservative",
          "Balanced",
          "Growth",
          "Aggressive Growth",
        ]}
      />
      <TextAreaField
        label="Desired Retirement Lifestyle"
        name="retirement_lifestyle_description"
        value={data.retirement_lifestyle_description}
        onChange={handleChange([
          "retirement_info",
          "retirement_lifestyle_description",
        ])}
      />
    </div>
    <div className="flex justify-between mt-8">
      <button
        onClick={prevStep}
        className="bg-slate-300 text-slate-800 py-2 px-4 rounded-md hover:bg-slate-400 transition"
      >
        Back
      </button>
      <button
        onClick={nextStep}
        className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition"
      >
        Next
      </button>
    </div>
  </div>
);

// A helper function to format keys for display
const formatKey = (key) => {
  return key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
};

// A recursive component to display nested summary data
const SummaryRenderer = ({ data, level = 0 }) => {
  return (
    <div className={`${level > 0 ? "pl-4" : ""}`}>
      {Object.entries(data).map(([key, value]) => {
        if (typeof value === "object" && value !== null) {
          if (Array.isArray(value)) {
            return (
              <div key={key} className="mt-2">
                <p className="font-semibold text-slate-700">
                  {formatKey(key)}:
                </p>
                {value.length > 0 ? (
                  <ul className="list-disc list-inside pl-4 text-slate-600">
                    {value.map((item, index) => (
                      <li key={index}>
                        {item.name} - ₹{item.target_amount}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500 pl-4">None</p>
                )}
              </div>
            );
          }
          return (
            <div key={key} className="mt-2">
              <p className="font-semibold text-slate-700">{formatKey(key)}:</p>
              <SummaryRenderer data={value} level={level + 1} />
            </div>
          );
        }
        return (
          <p key={key} className="text-slate-600">
            <span className="font-semibold text-slate-700">
              {formatKey(key)}:
            </span>{" "}
            {String(value) || "N/A"}
          </p>
        );
      })}
    </div>
  );
};

const Summary = ({ prevStep, formData, handleSubmit }) => (
  <div>
    <h2 className="text-2xl font-semibold mb-6 text-slate-800">
      Review Your Plan
    </h2>
    <div className="space-y-4 bg-slate-50 p-6 rounded-md">
      <SummaryRenderer data={formData} />
    </div>
    <div className="flex justify-between mt-8">
      <button
        onClick={prevStep}
        className="bg-slate-300 text-slate-800 py-2 px-4 rounded-md hover:bg-slate-400 transition"
      >
        Back
      </button>
      <button
        onClick={handleSubmit}
        className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition"
      >
        Submit Plan
      </button>
    </div>
  </div>
);

const Success = () => (
  <div className="text-center py-8">
    <h2 className="text-2xl font-semibold mb-4 text-slate-800">Thank You!</h2>
    <p className="text-slate-600">
      Your retirement plan has been submitted. We will be in touch shortly.
    </p>
  </div>
);

// --- Reusable Form Field Components ---
const InputField = ({ label, ...props }) => (
  <div>
    <label
      htmlFor={props.name}
      className="block text-sm font-medium text-gray-700 mb-1"
    >
      {label}
    </label>
    <input
      {...props}
      id={props.name}
      className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
    />
  </div>
);

const TextAreaField = ({ label, ...props }) => (
  <div>
    <label
      htmlFor={props.name}
      className="block text-sm font-medium text-gray-700 mb-1"
    >
      {label}
    </label>
    <textarea
      {...props}
      rows="3"
      id={props.name}
      className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
    />
  </div>
);

const SelectField = ({ label, options, ...props }) => (
  <div>
    <label
      htmlFor={props.name}
      className="block text-sm font-medium text-gray-700 mb-1"
    >
      {label}
    </label>
    <select
      {...props}
      id={props.name}
      className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
    >
      <option value="">Select an option</option>
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  </div>
);

export default P1;
