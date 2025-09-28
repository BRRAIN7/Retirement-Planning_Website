import React, { useState } from "react";

// Main App Component
const App = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // from retirement_plans
    userName: "",
    currentAge: "",
    desiredRetirementAge: "",
    monthlyIncomeInr: "",
    annualSavingsRatePercent: "",
    epfSavingsInr: "",
    ppfSavingsInr: "",
    npsSavingsInr: "",
    otherInvestmentsInr: "",
    elssAnnualInvestmentInr: "",
    totalDebtInr: "",
    debtRepaymentAnnualInr: "",
    emergencyFundInr: "",
    riskToleranceScore: 5,
    maritalStatus: "",
    numberOfChildren: "",
    retirementLifestyleDescription: "",
    investmentPreferences: "",
    desiredRetirementExpensesInr: "",
    // from goals tables
    shortTermGoals: [],
    midTermGoals: [],
    longTermGoals: [],
  });

  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);

  const handleChange = (input) => (e) => {
    setFormData({ ...formData, [input]: e.target.value });
  };

  // --- Goal Handlers ---
  const addGoal = (goalType) => {
    const newGoal = { goal_name: "", description: "" };
    setFormData((prev) => ({
      ...prev,
      [goalType]: [...prev[goalType], newGoal],
    }));
  };

  const removeGoal = (goalType, index) => {
    setFormData((prev) => ({
      ...prev,
      [goalType]: prev[goalType].filter((_, i) => i !== index),
    }));
  };

  const handleGoalChange = (goalType, index, e) => {
    const { name, value } = e.target;
    const updatedGoals = [...formData[goalType]];
    updatedGoals[index][name] = value;
    setFormData({ ...formData, [goalType]: updatedGoals });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real application, you would send this data to your backend API.
    console.log("Final Form Data:", formData);
    nextStep(); // Move to the success/thank you page
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <Step1
            nextStep={nextStep}
            handleChange={handleChange}
            formData={formData}
          />
        );
      case 2:
        return (
          <Step2
            nextStep={nextStep}
            prevStep={prevStep}
            handleChange={handleChange}
            formData={formData}
          />
        );
      case 3:
        return (
          <Step3
            nextStep={nextStep}
            prevStep={prevStep}
            handleChange={handleChange}
            formData={formData}
          />
        );
      case 4:
        return (
          <Step4
            nextStep={nextStep}
            prevStep={prevStep}
            handleGoalChange={handleGoalChange}
            addGoal={addGoal}
            removeGoal={removeGoal}
            formData={formData}
            goalType="shortTermGoals"
            title="Short-Term Goals"
          />
        );
      case 5:
        return (
          <Step4
            nextStep={nextStep}
            prevStep={prevStep}
            handleGoalChange={handleGoalChange}
            addGoal={addGoal}
            removeGoal={removeGoal}
            formData={formData}
            goalType="midTermGoals"
            title="Mid-Term Goals"
          />
        );
      case 6:
        return (
          <Step4
            nextStep={nextStep}
            prevStep={prevStep}
            handleGoalChange={handleGoalChange}
            addGoal={addGoal}
            removeGoal={removeGoal}
            formData={formData}
            goalType="longTermGoals"
            title="Long-Term Goals"
          />
        );
      case 7:
        return (
          <Step5
            nextStep={nextStep}
            prevStep={prevStep}
            handleChange={handleChange}
            formData={formData}
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
            handleChange={handleChange}
            formData={formData}
          />
        );
    }
  };

  const totalSteps = 9;
  const progress = (step / totalSteps) * 100;

  return (
    <div className="bg-slate-100 min-h-screen flex flex-col items-center justify-center font-sans p-4">
      <div className="w-full max-w-2xl">
        <h1 className="text-3xl font-bold text-center text-slate-700 mb-2">
          Retirement Planner
        </h1>
        <p className="text-center text-slate-500 mb-6">
          Let's build your financial future, one step at a time.
        </p>

        {/* Stepper Progress Bar */}
        <div className="flex items-center justify-between mb-8 px-4">
          {[...Array(totalSteps - 1)].map((_, i) => {
            const stepCompleted = i + 1 < step;
            const stepActive = i + 1 === step;
            return (
              <div key={i} className="flex-1 flex items-center">
                {/* Circle */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors duration-500 ${
                    stepCompleted
                      ? "bg-indigo-600 border-indigo-600 text-white"
                      : stepActive
                      ? "border-indigo-600 text-indigo-600"
                      : "border-slate-300 text-slate-500"
                  }`}
                >
                  {i + 1}
                </div>
                {/* Line */}
                {i < totalSteps - 2 && (
                  <div
                    className={`flex-1 h-1 transition-all duration-500 ${
                      i + 1 < step ? "bg-indigo-600" : "bg-slate-300"
                    }`}
                  ></div>
                )}
              </div>
            );
          })}
        </div>
        <div className="bg-white rounded-lg shadow-xl p-8">{renderStep()}</div>
      </div>
    </div>
  );
};

// --- Step Components ---

const Step1 = ({ nextStep, handleChange, formData }) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-slate-800">
        Basic Information
      </h2>
      <div className="space-y-4">
        <InputField
          label="Your Name"
          name="userName"
          value={formData.userName}
          onChange={handleChange("userName")}
        />
        <InputField
          label="Current Age"
          name="currentAge"
          type="number"
          value={formData.currentAge}
          onChange={handleChange("currentAge")}
        />
        <InputField
          label="Desired Retirement Age"
          name="desiredRetirementAge"
          type="number"
          value={formData.desiredRetirementAge}
          onChange={handleChange("desiredRetirementAge")}
        />
        <SelectField
          label="Marital Status"
          name="maritalStatus"
          value={formData.maritalStatus}
          onChange={handleChange("maritalStatus")}
          options={["Single", "Married", "Divorced", "Widowed"]}
        />
        <InputField
          label="Number of Children"
          name="numberOfChildren"
          type="number"
          value={formData.numberOfChildren}
          onChange={handleChange("numberOfChildren")}
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
};

const Step2 = ({ nextStep, prevStep, handleChange, formData }) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-slate-800">
        Financial Overview
      </h2>
      <div className="space-y-4">
        <InputField
          label="Monthly Income (INR)"
          name="monthlyIncomeInr"
          type="number"
          value={formData.monthlyIncomeInr}
          onChange={handleChange("monthlyIncomeInr")}
        />
        <InputField
          label="Annual Savings Rate (%)"
          name="annualSavingsRatePercent"
          type="number"
          value={formData.annualSavingsRatePercent}
          onChange={handleChange("annualSavingsRatePercent")}
        />
        <InputField
          label="Emergency Fund (INR)"
          name="emergencyFundInr"
          type="number"
          value={formData.emergencyFundInr}
          onChange={handleChange("emergencyFundInr")}
        />
        <InputField
          label="Total Debt (INR)"
          name="totalDebtInr"
          type="number"
          value={formData.totalDebtInr}
          onChange={handleChange("totalDebtInr")}
        />
        <InputField
          label="Annual Debt Repayment (INR)"
          name="debtRepaymentAnnualInr"
          type="number"
          value={formData.debtRepaymentAnnualInr}
          onChange={handleChange("debtRepaymentAnnualInr")}
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
};

const Step3 = ({ nextStep, prevStep, handleChange, formData }) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-slate-800">
        Investments & Savings
      </h2>
      <div className="space-y-4">
        <InputField
          label="EPF Savings (INR)"
          name="epfSavingsInr"
          type="number"
          value={formData.epfSavingsInr}
          onChange={handleChange("epfSavingsInr")}
        />
        <InputField
          label="PPF Savings (INR)"
          name="ppfSavingsInr"
          type="number"
          value={formData.ppfSavingsInr}
          onChange={handleChange("ppfSavingsInr")}
        />
        <InputField
          label="NPS Savings (INR)"
          name="npsSavingsInr"
          type="number"
          value={formData.npsSavingsInr}
          onChange={handleChange("npsSavingsInr")}
        />
        <InputField
          label="Other Investments (INR)"
          name="otherInvestmentsInr"
          type="number"
          value={formData.otherInvestmentsInr}
          onChange={handleChange("otherInvestmentsInr")}
        />
        <InputField
          label="Annual ELSS Investment (INR)"
          name="elssAnnualInvestmentInr"
          type="number"
          value={formData.elssAnnualInvestmentInr}
          onChange={handleChange("elssAnnualInvestmentInr")}
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
};

const Step4 = ({
  nextStep,
  prevStep,
  handleGoalChange,
  addGoal,
  removeGoal,
  formData,
  goalType,
  title,
}) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-slate-800">{title}</h2>
      {formData[goalType].map((goal, index) => (
        <div key={index} className="p-4 border rounded-md mb-4 relative">
          <button
            onClick={() => removeGoal(goalType, index)}
            className="absolute top-2 right-2 text-slate-400 hover:text-red-500"
          >
            &times;
          </button>
          <InputField
            label="Goal Name"
            name="goal_name"
            value={goal.goal_name}
            onChange={(e) => handleGoalChange(goalType, index, e)}
          />
          <TextAreaField
            label="Description"
            name="description"
            value={goal.description}
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
};

const Step5 = ({ nextStep, prevStep, handleChange, formData }) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-slate-800">
        Lifestyle & Preferences
      </h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Risk Tolerance (1-10)
          </label>
          <input
            type="range"
            min="1"
            max="10"
            name="riskToleranceScore"
            value={formData.riskToleranceScore}
            onChange={handleChange("riskToleranceScore")}
            className="w-full"
          />
          <p className="text-center">{formData.riskToleranceScore}</p>
        </div>
        <TextAreaField
          label="Desired Retirement Lifestyle"
          name="retirementLifestyleDescription"
          value={formData.retirementLifestyleDescription}
          onChange={handleChange("retirementLifestyleDescription")}
        />
        <TextAreaField
          label="Investment Preferences (e.g., Stocks, Bonds, Real Estate)"
          name="investmentPreferences"
          value={formData.investmentPreferences}
          onChange={handleChange("investmentPreferences")}
        />
        <InputField
          label="Desired Monthly Expenses in Retirement (INR)"
          name="desiredRetirementExpensesInr"
          type="number"
          value={formData.desiredRetirementExpensesInr}
          onChange={handleChange("desiredRetirementExpensesInr")}
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
};

const Summary = ({ prevStep, formData, handleSubmit }) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-slate-800">
        Review Your Plan
      </h2>
      <div className="space-y-2 bg-slate-50 p-4 rounded-md">
        {Object.entries(formData).map(([key, value]) => {
          if (typeof value === "object" && value !== null) {
            return (
              <div key={key}>
                <p className="font-semibold capitalize">
                  {key.replace(/([A-Z])/g, " $1")}:
                </p>
                {value.length > 0 ? (
                  <ul className="list-disc list-inside pl-4">
                    {value.map((item, index) => (
                      <li key={index}>
                        {item.goal_name}: {item.description}
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
            <p key={key}>
              <span className="font-semibold capitalize">
                {key.replace(/([A-Z])/g, " $1")}:
              </span>{" "}
              {String(value)}
            </p>
          );
        })}
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
};

const Success = () => (
  <div className="text-center">
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

export default App;
