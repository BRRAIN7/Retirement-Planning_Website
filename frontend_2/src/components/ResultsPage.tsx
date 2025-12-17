import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // ✅ ADD THIS
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  Home,
  TrendingUp,
  Target,
  AlertCircle,
  CheckCircle2,
  Calendar,
  MessageCircle, // ✅ ADD THIS
} from "lucide-react";

const ResultsPage = ({
  results,
  onBackToHome,
}: {
  results: any;
  onBackToHome: () => void;
}) => {
  const navigate = useNavigate(); // ✅ initialize navigation

  const [agentOutput, setAgentOutput] = useState<string>("Loading insights...");
  const [overview, setOverview] = useState({
    yearsToRetirement: 0,
    currentAssets: 0,
    retirementGoal: 0,
    riskTolerance: "N/A",
  });
  const [projection, setProjection] = useState({
    currentAssets: 0,
    monthlyContribution: 0,
    projectedAtRetirement: 0,
    savingsGap: 0,
  });

  // 🎯 Compute Data
  useEffect(() => {
    if (results) {
      const {
        yearsToRetirement,
        currentAssets,
        retirementGoal,
        riskTolerance,
      } = results;
      const monthlyContribution = 50000;
      const r = 0.06;
      const n = yearsToRetirement;
      let projectedAtRetirement = currentAssets;
      for (let i = 0; i < n; i++) {
        projectedAtRetirement =
          (projectedAtRetirement + monthlyContribution * 12) * (1 + r);
      }
      const savingsGap = retirementGoal - projectedAtRetirement;

      setOverview({
        yearsToRetirement,
        currentAssets,
        retirementGoal,
        riskTolerance,
      });

      setProjection({
        currentAssets,
        monthlyContribution,
        projectedAtRetirement,
        savingsGap,
      });
    }
  }, [results]);

  // 🤖 Fetch AI insights
  useEffect(() => {
    if (results) {
      fetch("http://127.0.0.1:5000/ai_insights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(results),
      })
        .then((res) => res.json())
        .then((data) => {
          setAgentOutput(
            data.message || data.output || "No insights available."
          );
        })
        .catch((err) => {
          console.error("AI insight error:", err);
          setAgentOutput(
            "⚠️ Unable to fetch insights. Please try again later."
          );
        });
    }
  }, [results]);

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <h2>No results found. Please complete your assessment first.</h2>
      </div>
    );
  }

  const goalProgress = (overview.currentAssets / overview.retirementGoal) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5 py-12">
      <div className="container mx-auto max-w-6xl px-4">
        {/* ✅ Header */}
        <div className="mb-10 text-center">
          <div className="mb-4 inline-flex items-center justify-center rounded-full bg-success/10 p-3">
            <CheckCircle2 className="h-8 w-8 text-success" />
          </div>
          <h1 className="text-4xl font-bold">Retirement Overview</h1>
          <p className="text-muted-foreground mt-2">
            Here’s your complete personalized retirement and investment analysis.
          </p>
        </div>

        {/* 🧾 Summary Cards */}
        <div className="grid gap-4 md:grid-cols-4 mb-8">
          <Card>
            <CardHeader>
              <CardDescription>Years to Retirement</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center gap-2 text-2xl font-bold text-primary">
              <Calendar className="h-5 w-5" /> {overview.yearsToRetirement}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Current Assets</CardDescription>
            </CardHeader>
            <CardContent className="text-2xl font-bold text-green-600">
              {formatCurrency(overview.currentAssets)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Retirement Goal</CardDescription>
            </CardHeader>
            <CardContent className="text-2xl font-bold text-blue-600">
              {formatCurrency(overview.retirementGoal)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Risk Tolerance</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge
                variant={
                  overview.riskTolerance === "Aggressive"
                    ? "default"
                    : overview.riskTolerance === "Balanced"
                    ? "secondary"
                    : "outline"
                }
              >
                {overview.riskTolerance}
              </Badge>
            </CardContent>
          </Card>
        </div>

        {/* 💡 AI Insights */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle>AI Advisor Insights</CardTitle>
            <CardDescription>
              Smart suggestions tailored to your financial profile
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground whitespace-pre-line leading-relaxed">
              {agentOutput}
            </p>

            {/* ✅ Continue Chatting Button */}
            <div className="mt-6 flex justify-end">
              <Button
                onClick={() =>
                  navigate("/chat", {
                    state: { initialMessage: agentOutput }, // 👈 pass the AI insight
                  })
                }
                className="gap-2"
              >
                <MessageCircle className="h-4 w-4" />
                Continue Chatting
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 📈 Projection Section */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle>Projected Savings</CardTitle>
            <CardDescription>
              Projection based on your savings and returns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p>Current Assets</p>
                <h3 className="text-2xl font-semibold text-green-600">
                  {formatCurrency(projection.currentAssets)}
                </h3>
              </div>
              <div>
                <p>Monthly Contribution</p>
                <h3 className="text-2xl font-semibold text-blue-600">
                  {formatCurrency(projection.monthlyContribution)}
                </h3>
              </div>
              <div>
                <p>Projected at Retirement</p>
                <h3 className="text-2xl font-semibold text-green-700">
                  {formatCurrency(projection.projectedAtRetirement)}
                </h3>
              </div>
              <div>
                <p>Savings Gap</p>
                <h3
                  className={`text-2xl font-semibold ${
                    projection.savingsGap > 0
                      ? "text-red-600"
                      : "text-green-600"
                  }`}
                >
                  {formatCurrency(projection.savingsGap)}
                </h3>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 🎯 Retirement Goal Progress */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle>Goal Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={goalProgress} className="h-3" />
            <p className="mt-2 text-sm text-muted-foreground">
              {goalProgress.toFixed(1)}% of your retirement goal achieved
            </p>
          </CardContent>
        </Card>

        {/* 🧩 Recommendations */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>
              AI-generated suggestions to improve your plan
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <ol className="list-decimal ml-5 space-y-2">
              <li>Increase your monthly savings rate to close the gap.</li>
              <li>Diversify across equity, debt, and gold.</li>
              <li>Review your asset allocation annually.</li>
            </ol>
          </CardContent>
        </Card>

        {/* ⚠️ Important Note */}
        <Card className="mb-8 border-info/50 bg-info/5">
          <CardContent className="flex gap-3 pt-6">
            <AlertCircle className="h-5 w-5 shrink-0 text-info" />
            <div className="space-y-1">
              <p className="font-medium">Important Note</p>
              <p className="text-sm text-muted-foreground">
                These recommendations are generated by AI based on your inputs.
                Please consult a certified financial advisor before taking major
                financial decisions.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* ⚡ Actions */}
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Button size="lg" onClick={onBackToHome} className="gap-2">
            <Home className="h-4 w-4" />
            Back to Home
          </Button>
          <Button size="lg" variant="outline" className="gap-2">
            <TrendingUp className="h-4 w-4" />
            Download Report
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
