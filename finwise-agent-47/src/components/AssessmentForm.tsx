import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, ArrowRight, Loader2 } from "lucide-react";
import { toast } from "sonner";

const AssessmentForm = ({
  onComplete,
}: {
  onComplete: (results: any) => void;
}) => {
  const [step, setStep] = useState(1);
  const totalSteps = 9;
  const effectiveSteps = totalSteps - 1;
  const progress = Math.min(100, (step / effectiveSteps) * 100);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    personal_info: {
      name: "",
      current_age: "",
      gender: "",
      marital_status: "",
      number_of_children: "",
    },
    financial_info: {
      income: { annual: "" },
      expenses: {
        monthly_total: "",
        components: { loan_emis: "", investment_sips: "", misc: "" },
      },
      assets: {
        savings: { epf: "", ppf: "", nps: "", bank_savings: "" },
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

  const stepMeta = [
    {
      title: "Personal Information",
      description: "Tell us a bit about yourself and your family.",
    },
    {
      title: "Income & Expenses",
      description: "Share your income and expense structure.",
    },
    {
      title: "Assets & Investments",
      description: "Provide details about your savings and investments.",
    },
    {
      title: "Short-Term Goals",
      description: "Your 1-3 year financial goals.",
    },
    { title: "Medium-Term Goals", description: "Your 3-7 year goals." },
    { title: "Long-Term Goals", description: "Your 7+ year aspirations." },
    {
      title: "Retirement Preferences",
      description: "Your preferences for retirement.",
    },
    {
      title: "Review & Confirm",
      description: "Review your inputs before submitting.",
    },
  ];

  const nextStep = () => step < totalSteps && setStep(step + 1);
  const prevStep = () => step > 1 && setStep(step - 1);

  // ---- Nested state update helper ----
  const updateNestedValue = (path: string[], val: any) => {
    setFormData((prev) => {
      const copy = JSON.parse(JSON.stringify(prev));
      let curr = copy;
      for (let i = 0; i < path.length - 1; i++) curr = curr[path[i]];
      curr[path[path.length - 1]] = val;
      return copy;
    });
  };

  const handleNestedChange =
    (path: string[]) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      updateNestedValue(path, e.target.value);
    };

  const handleNestedSelectChange = (path: string[]) => (value: string) => {
    updateNestedValue(path, value);
  };

  const handleNestedSliderChange = (path: string[]) => (value: number[]) => {
    updateNestedValue(path, value[0]);
  };

  // ---- Goals ----
  const addGoal = (type: "short_term" | "medium_term" | "long_term") => {
    setFormData((prev) => ({
      ...prev,
      goals: {
        ...prev.goals,
        [type]: [...prev.goals[type], { name: "", target_amount: "" }],
      },
    }));
  };

  const removeGoal = (
    type: "short_term" | "medium_term" | "long_term",
    index: number
  ) => {
    setFormData((prev) => ({
      ...prev,
      goals: {
        ...prev.goals,
        [type]: prev.goals[type].filter((_, i) => i !== index),
      },
    }));
  };

  const handleGoalChange = (
    type: "short_term" | "medium_term" | "long_term",
    index: number,
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const updated = [...formData.goals[type]];
    updated[index][e.target.name] = e.target.value;

    setFormData((prev) => ({
      ...prev,
      goals: { ...prev.goals, [type]: updated },
    }));
  };

  // ---- Submit ----
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // 🔥 1. Try backend
      console.log(JSON.stringify(formData));
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/api/submit/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Backend error");

      const data = await response.json();

      toast.success("Plan submitted successfully!");

      // 🔥 2. Send real results to router
      onComplete({
        formData,
        aiPlan: data.plan,
      });
    } catch (err) {
      console.warn("Backend not responding — using fallback result");

      // 🔥 3. SAME fallback design as your previous form
      const mockResults = {
        yearsToRetirement: Math.max(
          0,
          Number(formData.retirement_info.desired_retirement_age || 60) -
            Number(formData.personal_info.current_age || 30)
        ),

        currentAssets:
          Number(formData.financial_info.assets.savings.epf || 0) +
          Number(formData.financial_info.assets.savings.ppf || 0) +
          Number(formData.financial_info.assets.savings.nps || 0) +
          Number(formData.financial_info.assets.savings.bank_savings || 0) +
          Number(formData.financial_info.assets.total_investments || 0),

        retirementGoal: 10000000,

        riskTolerance: formData.retirement_info.risk_tolerance_score,

        recommendations: [
          "Increase SIP investments monthly to accelerate retirement savings",
          "Aim for a diversified allocation across equity, debt, and gold",
          "Build an emergency fund covering at least 6 months of expenses",
          "Review all high-interest loans and plan fast repayment",
        ],
      };

      // 🔥 4. Simulate slight delay for more natural fallback UI
      setTimeout(() => {
        toast.success("Plan submitted using sample analysis!");
        onComplete(mockResults);
      }, 900);
    }

    setIsSubmitting(false);
  };

  // ---- Summary Renderer ----
  const SummaryRenderer = ({
    data,
    level = 0,
  }: {
    data: any;
    level?: number;
  }) => (
    <div className={level ? "pl-4" : ""}>
      {Object.entries(data).map(([key, val]) => {
        if (typeof val === "object" && val !== null) {
          if (Array.isArray(val)) {
            return (
              <div key={key}>
                <p className="font-semibold">{key.replace(/_/g, " ")}:</p>
                {val.length ? (
                  <ul className="list-disc pl-4">
                    {val.map((item, i) => (
                      <li key={i}>
                        {item.name} – ₹{item.target_amount}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm pl-4 text-muted">None</p>
                )}
              </div>
            );
          }
          return (
            <div key={key}>
              <p className="font-semibold">{key.replace(/_/g, " ")}:</p>
              <SummaryRenderer data={val} level={level + 1} />
            </div>
          );
        }
        return (
          <p key={key}>
            <strong>{key.replace(/_/g, " ")}:</strong>{" "}
            {String(val) !== "" ? String(val) : "N/A"}
          </p>
        );
      })}
    </div>
  );

  // ---- Step Renderer ----
  const renderStepContent = () => {
    const { personal_info, financial_info, goals, retirement_info } = formData;

    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <Label>Your Name</Label>
            <Input
              value={personal_info.name}
              onChange={handleNestedChange(["personal_info", "name"])}
            />

            <Label>Current Age</Label>
            <Input
              type="number"
              value={personal_info.current_age}
              onChange={handleNestedChange(["personal_info", "current_age"])}
            />

            <Label>Gender</Label>
            <Select
              value={personal_info.gender}
              onValueChange={handleNestedSelectChange([
                "personal_info",
                "gender",
              ])}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Male">Male</SelectItem>
                <SelectItem value="Female">Female</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>

            <Label>Marital Status</Label>
            <Select
              value={personal_info.marital_status}
              onValueChange={handleNestedSelectChange([
                "personal_info",
                "marital_status",
              ])}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Single">Single</SelectItem>
                <SelectItem value="Married">Married</SelectItem>
                <SelectItem value="Divorced">Divorced</SelectItem>
              </SelectContent>
            </Select>

            <Label>Number of Children</Label>
            <Input
              type="number"
              value={personal_info.number_of_children}
              onChange={handleNestedChange([
                "personal_info",
                "number_of_children",
              ])}
            />
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <Label>Annual Income (₹)</Label>
            <Input
              type="number"
              value={financial_info.income.annual}
              onChange={handleNestedChange([
                "financial_info",
                "income",
                "annual",
              ])}
            />

            <Label>Monthly Expenses (₹)</Label>
            <Input
              type="number"
              value={financial_info.expenses.monthly_total}
              onChange={handleNestedChange([
                "financial_info",
                "expenses",
                "monthly_total",
              ])}
            />

            <Label>Loan EMIs (₹)</Label>
            <Input
              type="number"
              value={financial_info.expenses.components.loan_emis}
              onChange={handleNestedChange([
                "financial_info",
                "expenses",
                "components",
                "loan_emis",
              ])}
            />

            <Label>Investment SIPs (₹)</Label>
            <Input
              type="number"
              value={financial_info.expenses.components.investment_sips}
              onChange={handleNestedChange([
                "financial_info",
                "expenses",
                "components",
                "investment_sips",
              ])}
            />

            <Label>Misc Expenses (₹)</Label>
            <Input
              type="number"
              value={financial_info.expenses.components.misc}
              onChange={handleNestedChange([
                "financial_info",
                "expenses",
                "components",
                "misc",
              ])}
            />

            <Label>Total Debt (₹)</Label>
            <Input
              type="number"
              value={financial_info.liabilities.total_debt}
              onChange={handleNestedChange([
                "financial_info",
                "liabilities",
                "total_debt",
              ])}
            />

            <Label>Monthly Debt Contribution (₹)</Label>
            <Input
              type="number"
              value={financial_info.liabilities.monthly_debt_contribution}
              onChange={handleNestedChange([
                "financial_info",
                "liabilities",
                "monthly_debt_contribution",
              ])}
            />
          </div>
        );

      case 3:
        const a = financial_info.assets;
        return (
          <div className="space-y-4">
            <Label>EPF (₹)</Label>
            <Input
              value={a.savings.epf}
              onChange={handleNestedChange([
                "financial_info",
                "assets",
                "savings",
                "epf",
              ])}
            />

            <Label>PPF (₹)</Label>
            <Input
              value={a.savings.ppf}
              onChange={handleNestedChange([
                "financial_info",
                "assets",
                "savings",
                "ppf",
              ])}
            />

            <Label>NPS (₹)</Label>
            <Input
              value={a.savings.nps}
              onChange={handleNestedChange([
                "financial_info",
                "assets",
                "savings",
                "nps",
              ])}
            />

            <Label>Bank Savings (₹)</Label>
            <Input
              value={a.savings.bank_savings}
              onChange={handleNestedChange([
                "financial_info",
                "assets",
                "savings",
                "bank_savings",
              ])}
            />

            <Label>Total Investments (₹)</Label>
            <Input
              value={a.total_investments}
              onChange={handleNestedChange([
                "financial_info",
                "assets",
                "total_investments",
              ])}
            />

            <Label>Emergency Fund (₹)</Label>
            <Input
              value={a.emergency_fund}
              onChange={handleNestedChange([
                "financial_info",
                "assets",
                "emergency_fund",
              ])}
            />

            {/* Portfolio Breakdown */}
            {Object.keys(a.portfolio_breakdown_percent).map((key) => (
              <div key={key}>
                <Label>{key}</Label>
                <Input
                  type="number"
                  value={a.portfolio_breakdown_percent[key]}
                  onChange={handleNestedChange([
                    "financial_info",
                    "assets",
                    "portfolio_breakdown_percent",
                    key,
                  ])}
                />
              </div>
            ))}
          </div>
        );

      case 4:
      case 5:
      case 6:
        const type =
          step === 4 ? "short_term" : step === 5 ? "medium_term" : "long_term";
        const list = goals[type];

        return (
          <div className="space-y-4">
            {list.map((g, i) => (
              <div key={i} className="relative p-4 bg-muted/50 rounded">
                <button
                  type="button"
                  onClick={() => removeGoal(type, i)}
                  className="absolute right-2 top-2 text-xs text-muted-foreground hover:text-red-500"
                >
                  Remove
                </button>

                <Label>Goal Name</Label>
                <Input
                  name="name"
                  value={g.name}
                  onChange={(e) => handleGoalChange(type, i, e)}
                />

                <Label>Target Amount (₹)</Label>
                <Input
                  type="number"
                  name="target_amount"
                  value={g.target_amount}
                  onChange={(e) => handleGoalChange(type, i, e)}
                />
              </div>
            ))}

            <Button variant="outline" onClick={() => addGoal(type)}>
              + Add Goal
            </Button>
          </div>
        );

      case 7:
        return (
          <div className="space-y-4">
            <Label>Desired Retirement Age</Label>
            <Input
              value={retirement_info.desired_retirement_age}
              onChange={handleNestedChange([
                "retirement_info",
                "desired_retirement_age",
              ])}
            />

            <Label>Retirement Monthly Expenses (₹)</Label>
            <Input
              value={retirement_info.desired_retirement_expenses_inr}
              onChange={handleNestedChange([
                "retirement_info",
                "desired_retirement_expenses_inr",
              ])}
            />

            <Label>Annual Savings Rate (%)</Label>
            <Input
              value={retirement_info.annual_savings_rate_percent}
              onChange={handleNestedChange([
                "retirement_info",
                "annual_savings_rate_percent",
              ])}
            />

            <Label>
              Risk Tolerance ({retirement_info.risk_tolerance_score})
            </Label>
            <Slider
              min={1}
              max={10}
              step={1}
              value={[retirement_info.risk_tolerance_score]}
              onValueChange={handleNestedSliderChange([
                "retirement_info",
                "risk_tolerance_score",
              ])}
            />

            <Label>Investment Preference</Label>
            <Select
              value={retirement_info.investment_preferences}
              onValueChange={handleNestedSelectChange([
                "retirement_info",
                "investment_preferences",
              ])}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a preference" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Saving">Saving</SelectItem>
                <SelectItem value="Conservative">Conservative</SelectItem>
                <SelectItem value="Balanced">Balanced</SelectItem>
                <SelectItem value="Growth">Growth</SelectItem>
                <SelectItem value="Aggressive Growth">
                  Aggressive Growth
                </SelectItem>
              </SelectContent>
            </Select>

            <Label>Lifestyle Description</Label>
            <Textarea
              rows={3}
              value={retirement_info.retirement_lifestyle_description}
              onChange={handleNestedChange([
                "retirement_info",
                "retirement_lifestyle_description",
              ])}
            />
          </div>
        );

      case 8:
        return (
          <div className="space-y-4">
            <div className="bg-muted/50 p-4 rounded max-h-[400px] overflow-y-auto">
              <SummaryRenderer data={formData} />
            </div>
            <p className="text-xs text-muted-foreground">
              Review before submitting.
            </p>
          </div>
        );

      default:
        return null;
    }
  };

  // ---- UI ----
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-accent/10 px-4 py-12">
      <Card className="w-full max-w-3xl shadow-xl">
        <CardHeader>
          <div className="mb-4">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>
                Step {step} of {effectiveSteps}
              </span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
          <CardTitle className="text-2xl">
            {stepMeta[step - 1]?.title}
          </CardTitle>
          <CardDescription>{stepMeta[step - 1]?.description}</CardDescription>
        </CardHeader>

        <CardContent>
          <form
            onSubmit={step === 8 ? handleSubmit : (e) => e.preventDefault()}
            className="space-y-6"
          >
            {renderStepContent()}

            <div className="flex gap-4">
              {step > 1 && step <= 8 && (
                <Button
                  variant="outline"
                  onClick={prevStep}
                  disabled={isSubmitting}
                  className="flex-1"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" /> Back
                </Button>
              )}

              {step < 8 && (
                <Button
                  onClick={nextStep}
                  disabled={isSubmitting}
                  className="flex-1"
                >
                  Next <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              )}

              {step === 8 && (
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    "Submit Plan"
                  )}
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default AssessmentForm;
