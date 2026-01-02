import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Home,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Calendar,
  MessageCircle,
} from "lucide-react";

const ResultsPage = ({
  results,
  onBackToHome,
}: {
  results: any;
  onBackToHome: () => void;
}) => {
  const navigate = useNavigate();
  console.log("RESULTS RECEIVED:", results);
  const [overview, setOverview] = useState({
    yearsToRetirement: 0,
    currentAssets: 0,
    retirementGoal: 0,
  });

  const [projection, setProjection] = useState({
    currentAssets: 0,
    monthlyContribution: 0,
    projectedAtRetirement: 0,
    savingsGap: 0,
  });

  const [agentOutput, setAgentOutput] = useState<string>("");

  const formatCurrency = (amount?: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount ?? 0);

  useEffect(() => {
    if (!results || !results.backendResult) return;

    const data = results.backendResult;
    const m = data.metrics;

    if (!m) return;

    setOverview({
      yearsToRetirement: m.years_to_retirement ?? 0,
      currentAssets: m.projected_future_assets ?? 0,
      retirementGoal: m.gross_retirement_corpus ?? 0,
    });

    setProjection({
      currentAssets: m.projected_future_assets ?? 0,
      monthlyContribution: m.required_retirement_sip ?? 0,
      projectedAtRetirement: m.projected_future_assets ?? 0,
      savingsGap: m.net_corpus_to_build ?? 0,
    });

    setAgentOutput(data.plan ?? "");
  }, [results]);


  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <h2>No results found. Please complete your assessment first.</h2>
      </div>
    );
  }

  const goalProgress =
    overview.retirementGoal > 0
      ? (overview.currentAssets / overview.retirementGoal) * 100
      : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5 py-12">
      <div className="container mx-auto max-w-6xl px-4">
        {/* Header */}
        <div className="mb-10 text-center">
          <div className="mb-4 inline-flex items-center justify-center rounded-full bg-success/10 p-3">
            <CheckCircle2 className="h-8 w-8 text-success" />
          </div>
          <h1 className="text-4xl font-bold">Retirement Overview</h1>
          <p className="text-muted-foreground mt-2">
            Here’s your complete personalized retirement and investment
            analysis.
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <Card>
            <CardHeader>
              <CardDescription>Years to Retirement</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center gap-2 text-2xl font-bold text-primary">
              <Calendar className="h-5 w-5" />
              {overview.yearsToRetirement}
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
        </div>

        {/* AI Insights */}
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

            <div className="mt-6 flex justify-end">
              <Button
                onClick={() =>
                  navigate("/chat", {
                    state: { initialMessage: agentOutput },
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

        {/* Projection */}
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

        {/* Goal Progress */}
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

        {/* Important Note */}
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

        {/* Actions */}
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
