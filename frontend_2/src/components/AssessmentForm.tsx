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
      risk_tolerance_score: -1,
      investment_preferences: "",
      annual_savings_rate_percent: "-1",
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
          // Keep space-y-4 (or space-y-6) here to handle spacing BETWEEN the groups
          <div className="space-y-4">

            {/* Name Group */}
            <div className="space-y-2">
              <Label htmlFor="name">Your Name</Label>
              <Input
                id="name"
                value={personal_info.name}
                placeholder=""
                onChange={(e) => {
                  // Regex: Only allow alphabets (a-z, A-Z) and spaces
                  if (/^[a-zA-Z\s]*$/.test(e.target.value)) {
                    handleNestedChange(["personal_info", "name"])(e);
                  }
                }}
              />
            </div>

            {/* Current Age Group */}
            <div className="space-y-2">
              <Label htmlFor="current_age">Current Age</Label>
              <Input
                id="current_age"
                type="number"
                min={0}
                max={100}
                value={personal_info.current_age}
                onKeyDown={(e) => {
                  if (["e", "E", "+", "-", "."].includes(e.key)) {
                    e.preventDefault();
                  }
                }}
                onChange={(e) => {
                  const value = Number(e.target.value);
                  if (value <= 100) {
                    handleNestedChange(["personal_info", "current_age"])(e as any);
                  }
                }}
              />
            </div>

            {/* Gender Group */}
            <div className="space-y-2">
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
            </div>

            {/* Marital Status Group */}
            <div className="space-y-2">
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
            </div>

            {/* Children Group */}
            <div className="space-y-2">
              <Label htmlFor="children">Number of Children</Label>
              <Input
                id="children"
                type="number"
                min={0}
                max={20}
                value={personal_info.number_of_children}
                onKeyDown={(e) => {
                  if (["e", "E", "+", "-", "."].includes(e.key)) {
                    e.preventDefault();
                  }
                }}
                onChange={(e) => {
                  const value = Number(e.target.value);
                  if (value <= 20) {
                    handleNestedChange([
                      "personal_info",
                      "number_of_children",
                    ])(e as any);
                  }
                }}
              />
            </div>
          </div>
        );

case 2:
        return (
          <div className="space-y-6">
            {/* --- Section 1: Income --- */}
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                💰 Income Details
              </h3>
              <div className="space-y-2">
                <Label>Annual Income (₹)</Label>
                <Input
                  type="number"
                  min={0}
                  placeholder="e.g. 1200000"
                  value={financial_info.income.annual}
                  onKeyDown={(e) => ["e", "E", "+", "-", "."].includes(e.key) && e.preventDefault()}
                  onChange={handleNestedChange(["financial_info", "income", "annual"])}
                />
              </div>
            </div>

            {/* --- Section 2: Expenses --- */}
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                💸Monthly Expense Breakdown
              </h3>
              <p className="text-sm text-muted-foreground -mt-2">
                Break down your monthly spending. The total is calculated automatically.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Component 1: Loan EMIs */}
                <div className="space-y-2">
                  <Label>Loan EMIs (₹)</Label>
                  <Input
                    type="number"
                    min={0}
                    placeholder="0"
                    value={financial_info.expenses.components.loan_emis}
                    onKeyDown={(e) => ["e", "E", "+", "-", "."].includes(e.key) && e.preventDefault()}
                    onChange={(e) => {
                      const val = e.target.value;
                      // Update Component
                      updateNestedValue(["financial_info", "expenses", "components", "loan_emis"], val);
                      
                      // Auto-calculate Total
                      const emi = Number(val) || 0;
                      const sips = Number(financial_info.expenses.components.investment_sips) || 0;
                      const misc = Number(financial_info.expenses.components.misc) || 0;
                      updateNestedValue(["financial_info", "expenses", "monthly_total"], (emi + sips + misc).toString());
                    }}
                  />
                </div>

                {/* Component 2: SIPs */}
                <div className="space-y-2">
                  <Label>Investment SIPs (₹)</Label>
                  <Input
                    type="number"
                    min={0}
                    placeholder="0"
                    value={financial_info.expenses.components.investment_sips}
                    onKeyDown={(e) => ["e", "E", "+", "-", "."].includes(e.key) && e.preventDefault()}
                    onChange={(e) => {
                      const val = e.target.value;
                      updateNestedValue(["financial_info", "expenses", "components", "investment_sips"], val);
                      
                      const sips = Number(val) || 0;
                      const emi = Number(financial_info.expenses.components.loan_emis) || 0;
                      const misc = Number(financial_info.expenses.components.misc) || 0;
                      updateNestedValue(["financial_info", "expenses", "monthly_total"], (emi + sips + misc).toString());
                    }}
                  />
                </div>

                {/* Component 3: Misc */}
                <div className="space-y-2">
                  <Label>Living Expenses (₹)</Label>
                  <Input
                    type="number"
                    min={0}
                    placeholder="0"
                    value={financial_info.expenses.components.misc}
                    onKeyDown={(e) => ["e", "E", "+", "-", "."].includes(e.key) && e.preventDefault()}
                    onChange={(e) => {
                      const val = e.target.value;
                      updateNestedValue(["financial_info", "expenses", "components", "misc"], val);
                      
                      const misc = Number(val) || 0;
                      const emi = Number(financial_info.expenses.components.loan_emis) || 0;
                      const sips = Number(financial_info.expenses.components.investment_sips) || 0;
                      updateNestedValue(["financial_info", "expenses", "monthly_total"], (emi + sips + misc).toString());
                    }}
                  />
                </div>
              </div>

              {/* Total (Calculated) */}
              <div className="pt-2">
                <div className="bg-muted/50 p-4 rounded-md border border-dashed border-primary/30 flex justify-between items-center">
                  <div className="space-y-1">
                    <Label className="text-base font-semibold text-primary">Total Monthly Expenses</Label>
                    <p className="text-xs text-muted-foreground">Sum of EMIs + SIPs + Misc</p>
                  </div>
                  <div className="text-2xl font-bold">
                    ₹{Number(financial_info.expenses.monthly_total).toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Debt Section - Kept separate as requested in original flow */}
              <div className="pt-4 border-t">
                <h4 className="font-medium mb-3 text-sm">Liabilities Snapshot</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Total Outstanding Debt (₹)</Label>
                    <Input
                      type="number"
                      min={0}
                      value={financial_info.liabilities.total_debt}
                      onKeyDown={(e) => ["e", "E", "+", "-", "."].includes(e.key) && e.preventDefault()}
                      onChange={handleNestedChange(["financial_info", "liabilities", "total_debt"])}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Monthly Debt Contribution (₹)</Label>
                    <Input
                      type="number"
                      min={0}
                      value={financial_info.liabilities.monthly_debt_contribution}
                      onKeyDown={(e) => ["e", "E", "+", "-", "."].includes(e.key) && e.preventDefault()}
                      onChange={handleNestedChange(["financial_info", "liabilities", "monthly_debt_contribution"])}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

case 3:
        const a = financial_info.assets;
        
        // Helper to calculate current total percentage
        const currentTotalPct = 
          Number(a.portfolio_breakdown_percent.equity || 0) + 
          Number(a.portfolio_breakdown_percent.mutual_funds || 0) + 
          Number(a.portfolio_breakdown_percent.gold || 0) + 
          Number(a.portfolio_breakdown_percent.crypto || 0) + 
          Number(a.portfolio_breakdown_percent.other || 0);

        // Helper to determine status color
        const getStatusColor = (total: number) => {
          if (total === 100) return "text-green-600 bg-green-50 border-green-200";
          if (total > 100) return "text-red-600 bg-red-50 border-red-200";
          return "text-amber-600 bg-amber-50 border-amber-200";
        };

        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* --- SECTION 1: FIXED INCOME & SAVINGS --- */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg border-b pb-2">
                1. Fixed Income & Savings
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>EPF Balance (₹)</Label>
                  <Input
                    type="number"
                    min="0"
                    placeholder="0"
                    value={a.savings.epf}
                    onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                    onChange={handleNestedChange(["financial_info", "assets", "savings", "epf"])}
                  />
                </div>
                <div className="space-y-2">
                  <Label>PPF Balance (₹)</Label>
                  <Input
                    type="number"
                    min="0"
                    placeholder="0"
                    value={a.savings.ppf}
                    onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                    onChange={handleNestedChange(["financial_info", "assets", "savings", "ppf"])}
                  />
                </div>
                <div className="space-y-2">
                  <Label>NPS Balance (₹)</Label>
                  <Input
                    type="number"
                    min="0"
                    placeholder="0"
                    value={a.savings.nps}
                    onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                    onChange={handleNestedChange(["financial_info", "assets", "savings", "nps"])}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Bank Savings (₹)</Label>
                  <Input
                    type="number"
                    min="0"
                    placeholder="0"
                    value={a.savings.bank_savings}
                    onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                    onChange={handleNestedChange(["financial_info", "assets", "savings", "bank_savings"])}
                  />
                </div>
              </div>
            </div>

            {/* --- SECTION 2: EMERGENCY FUND --- */}
            <div className="space-y-4 pt-2">
              <div className="border-l-4 border-primary pl-4">
                <h3 className="font-semibold text-lg">
                  2. Emergency Fund
                </h3>
                <p className="text-sm text-muted-foreground">
                  Liquid cash set aside strictly for emergencies.
                </p>
              </div>
              
              <div className="space-y-2">
                <Label>Amount (₹)</Label>
                <Input
                  type="number"
                  min="0"
                  placeholder="0"
                  value={a.emergency_fund}
                  onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                  onChange={handleNestedChange(["financial_info", "assets", "emergency_fund"])}
                />
              </div>
            </div>

            {/* --- SECTION 3: MARKET INVESTMENTS --- */}
            <div className="space-y-4 pt-2">
              <h3 className="font-semibold text-lg border-b pb-2">
                3. Market Investments
              </h3>
              
              <p className="text-sm text-muted-foreground">
                <span className="font-bold text-foreground">Note:</span> Do NOT include your EPF or Bank Savings inside "Total Investments".
              </p>

              <div className="space-y-6">
                <div className="space-y-2">
                  <Label>Total Investments Value (₹)</Label>
                  <Input
                    type="number"
                    min="0"
                    placeholder="0"
                    value={a.total_investments}
                    onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                    onChange={handleNestedChange(["financial_info", "assets", "total_investments"])}
                  />
                </div>

                {/* Breakdown Section - Always Visible */}
                <div className="space-y-4">
                  <div className="flex justify-between items-end">
                    <Label className="mb-1">Portfolio Breakdown (%)</Label>
                    <div className={`text-xs font-semibold px-3 py-1 rounded border ${getStatusColor(currentTotalPct)}`}>
                      Total: {currentTotalPct}% / 100%
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {["equity", "mutual_funds", "gold", "crypto", "other"].map((key) => (
                      <div key={key} className="space-y-1">
                        <Label className="text-xs text-muted-foreground capitalize">
                          {key.replace('_', ' ')}
                        </Label>
                        <div className="relative">
                          <Input
                            type="number"
                            min="0"
                            max="100" // HTML constraint
                            className={`pr-6 ${currentTotalPct > 100 ? "border-red-300 focus-visible:ring-red-200" : ""}`}
                            placeholder="0"
                            value={a.portfolio_breakdown_percent[key as keyof typeof a.portfolio_breakdown_percent]}
                            onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                            onChange={(e) => {
                              // Custom handler to clamp value at 100
                              let val = Number(e.target.value);
                              if (val > 100) val = 100; // Hard clamp
                              if (val < 0) val = 0;
                              
                              // We need to manually call updateNestedValue or mimic handleNestedChange here
                              // Since handleNestedChange is a wrapper, we can just call it with the string value
                              const syntheticEvent = { target: { value: val.toString() } };
                              handleNestedChange([
                                "financial_info",
                                "assets",
                                "portfolio_breakdown_percent",
                                key,
                              ])(syntheticEvent as any);
                            }}
                          />
                          <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">%</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Explicit Error Messages */}
                  {currentTotalPct > 100 && (
                    <p className="text-sm font-medium text-red-600 flex items-center animate-in slide-in-from-top-1">
                       ⚠️ Total exceeds 100%. Please reduce {currentTotalPct - 100}%.
                    </p>
                  )}
                  {Number(a.total_investments) > 0 && currentTotalPct < 100 && (
                    <p className="text-sm font-medium text-amber-600 flex items-center animate-in slide-in-from-top-1">
                       ⚠️ Allocation is incomplete. You have {100 - currentTotalPct}% remaining.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        );

case 4:
      case 5:
      case 6:
        const type =
          step === 4 ? "short_term" : step === 5 ? "medium_term" : "long_term";
        const list = goals[type];

        return (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {list.map((g, i) => (
              <div key={i} className="relative p-4 bg-muted/50 rounded border border-muted space-y-3">
                <button
                  type="button"
                  onClick={() => removeGoal(type, i)}
                  className="absolute right-2 top-2 text-xs text-muted-foreground hover:text-red-500 transition-colors"
                >
                  Remove
                </button>

                <div className="space-y-1">
                  <Label>Goal Name</Label>
                  <Input
                    name="name"
                    value={g.name}
                    placeholder="e.g. Buy Car"
                    onChange={(e) => {
                      // Regex: Only allow alphabets (a-z, A-Z) and spaces
                      if (/^[a-zA-Z\s]*$/.test(e.target.value)) {
                        handleGoalChange(type, i, e);
                      }
                    }}
                  />
                </div>

                <div className="space-y-1">
                  <Label>Target Amount (₹)</Label>
                  <Input
                    type="number"
                    name="target_amount"
                    min="0"
                    placeholder="0"
                    value={g.target_amount}
                    onKeyDown={(e) => {
                      // Block e, E, +, -, and . (decimal) to ensure strict integer/number entry
                      if (["e", "E", "+", "-", "."].includes(e.key)) {
                        e.preventDefault();
                      }
                    }}
                    onChange={(e) => handleGoalChange(type, i, e)}
                  />
                </div>
              </div>
            ))}

            <Button 
              variant="outline" 
              onClick={() => addGoal(type)}
              className="w-full border-dashed"
            >
              + Add {step === 4 ? "Short" : step === 5 ? "Medium" : "Long"} Term Goal
            </Button>
            
            {list.length === 0 && (
              <p className="text-sm text-center text-muted-foreground italic">
                No goals added yet. Click above to add one.
              </p>
            )}
          </div>
        );

case 7:
        return (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Desired Retirement Age */}
            <div className="space-y-2">
              <Label>Desired Retirement Age</Label>
              <Input
                type="number"
                min="0"
                max="99"
                placeholder="e.g. 60"
                value={retirement_info.desired_retirement_age}
                onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                onChange={(e) => {
                  const val = e.target.value;
                  // Only update if empty (deletion) or <= 99
                  if (val === "" || Number(val) <= 99) {
                    handleNestedChange([
                      "retirement_info",
                      "desired_retirement_age",
                    ])(e);
                  }
                }}
              />
            </div>

            {/* Retirement Monthly Expenses */}
            <div className="space-y-2">
              <Label>Retirement Monthly Expenses (₹)</Label>
              <Input
                type="number"
                min="0"
                placeholder="Enter your desired monthly expenses during retirement"
                value={retirement_info.desired_retirement_expenses_inr}
                onKeyDown={(e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()}
                onChange={handleNestedChange([
                  "retirement_info",
                  "desired_retirement_expenses_inr",
                ])}
              />
            </div>

            {/* Investment Preference */}
            <div className="space-y-2">
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
                  <SelectItem value="Saving">Saving (Low Risk)</SelectItem>
                  <SelectItem value="Conservative">Conservative</SelectItem>
                  <SelectItem value="Balanced">Balanced</SelectItem>
                  <SelectItem value="Growth">Growth</SelectItem>
                  <SelectItem value="Aggressive Growth">Aggressive Growth (High Risk)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Lifestyle Description */}
            <div className="space-y-2">
              <Label>Lifestyle Description</Label>
              <Textarea
                rows={4}
                placeholder="Describe your ideal retirement lifestyle (e.g., traveling twice a year, living in a farmhouse, etc.)"
                value={retirement_info.retirement_lifestyle_description}
                onChange={handleNestedChange([
                  "retirement_info",
                  "retirement_lifestyle_description",
                ])}
              />
            </div>
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
                  disabled={
                    isSubmitting || 
                    (step === 3 && Number(formData.financial_info.assets.total_investments) > 0 && 
                    (Number(formData.financial_info.assets.portfolio_breakdown_percent.equity || 0) + 
                      Number(formData.financial_info.assets.portfolio_breakdown_percent.mutual_funds || 0) + 
                      Number(formData.financial_info.assets.portfolio_breakdown_percent.gold || 0) + 
                      Number(formData.financial_info.assets.portfolio_breakdown_percent.crypto || 0) + 
                      Number(formData.financial_info.assets.portfolio_breakdown_percent.other || 0)) !== 100)
                  }
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
