import React, { useEffect, useState, useRef } from "react";
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
  Sparkles,
} from "lucide-react";

// --- CUSTOM FORMATTER (Updated for Tighter Spacing) ---
const FormattedText = ({ text }: { text: string }) => {
  if (!text) return null;

  const renderBold = (line: string) => {
    const parts = line.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-bold text-foreground">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    // Changed: space-y-3 -> space-y-1, leading-relaxed -> leading-normal
    <div className="space-y-1 text-muted-foreground leading-normal">
      {text.split("\n").map((line, index) => {
        // 1. Handle Headers (###)
        if (line.startsWith("### ")) {
          return (
            // Changed: mt-6 -> mt-3, mb-2 -> mb-1
            <h3 key={index} className="text-lg font-semibold text-primary mt-3 mb-1">
              {line.replace("### ", "")}
            </h3>
          );
        }
        // 2. Handle Lists (- )
        if (line.trim().startsWith("- ")) {
          return (
            <div key={index} className="flex gap-2 ml-2">
              <span className="text-primary">•</span>
              <p>{renderBold(line.replace("- ", ""))}</p>
            </div>
          );
        }
        // 3. Handle Empty Lines
        if (line.trim() === "") {
          // Changed: h-2 -> h-1 (Just a small spacer)
          return <div key={index} className="h-1"></div>;
        }
        // 4. Standard Paragraph
        return <p key={index}>{renderBold(line)}</p>;
      })}
    </div>
  );
};

// --- SUB-COMPONENT: STREAMING WRAPPER ---
const StreamedContent = ({ content }: { content: string }) => {
  const [displayedContent, setDisplayedContent] = useState("");
  const indexRef = useRef(0);

  useEffect(() => {
    setDisplayedContent("");
    indexRef.current = 0;
  }, [content]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      if (indexRef.current < content.length) {
        // Typing speed: 2 chars per 10ms
        const chunk = content.slice(indexRef.current, indexRef.current + 2);
        setDisplayedContent((prev) => prev + chunk);
        indexRef.current += 2;
      } else {
        clearInterval(intervalId);
      }
    }, 10); 

    return () => clearInterval(intervalId);
  }, [content]);

  return (
    <div>
      <FormattedText text={displayedContent} />
      {displayedContent.length < content.length && (
        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse align-middle"></span>
      )}
    </div>
  );
};

// --- MAIN PAGE COMPONENT ---
const ResultsPage = ({
  results,
  onBackToHome,
}: {
  results: any;
  onBackToHome: () => void;
}) => {
  const navigate = useNavigate();
  
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
    const formData = results.formData || {};
    const m = data.metrics;

    if (!m) return;

    // 1. Calculate Actual Monthly Contribution (Income - Expenses)
    const annualIncome = Number(formData.financial_info?.income?.annual || 0);
    const monthlyExpenses = Number(formData.financial_info?.expenses?.monthly_total || 0);
    const calculatedSurplus = (annualIncome / 12) - monthlyExpenses;
    const monthlyContribution = Math.max(0, calculatedSurplus);

    // 2. Set Overview & Projection
    setOverview({
      yearsToRetirement: m.years_to_retirement ?? 0,
      currentAssets: m.projected_future_assets ?? 0,
      retirementGoal: m.gross_retirement_corpus ?? 0,
    });

    setProjection({
      currentAssets: m.projected_future_assets ?? 0,
      monthlyContribution: monthlyContribution,
      projectedAtRetirement: m.projected_future_assets ?? 0,
      savingsGap: m.net_corpus_to_build ?? 0,
    });

    // 3. Set Agent Output
    setAgentOutput(data.plan ?? "Analyzing your financial profile...");
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
        <div className="mb-10 text-center animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="mb-4 inline-flex items-center justify-center rounded-full bg-success/10 p-3">
            <CheckCircle2 className="h-8 w-8 text-success" />
          </div>
          <h1 className="text-4xl font-bold">Retirement Overview</h1>
          <p className="text-muted-foreground mt-2">
            Here’s your complete personalized retirement and investment analysis.
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-3 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
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
        <Card className="mb-10 shadow-lg border-primary/10 animate-in fade-in zoom-in-95 duration-700 delay-200">
          <CardHeader className="bg-primary/5 border-b border-primary/10">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary animate-pulse" />
              <CardTitle>AI Advisor Insights</CardTitle>
            </div>
            <CardDescription>
              Personalized strategy tailored to your profile
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 md:p-8 bg-card">
            {agentOutput ? (
              <StreamedContent content={agentOutput} />
            ) : (
              <div className="flex items-center gap-2 text-muted-foreground italic">
                <span className="animate-spin">⏳</span> Generating financial plan...
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-8 flex justify-end pt-4 border-t">
              <Button
                onClick={() =>
                  navigate("/chat", {
                    state: { initialMessage: agentOutput },
                  })
                }
                className="gap-2"
              >
                <MessageCircle className="h-4 w-4" />
                Ask Follow-up Questions
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Projection Data */}
        <Card className="mb-10 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
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
                <p className="text-xs text-muted-foreground">(Income - Expenses)</p>
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
        <Card className="mb-10 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-500">
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

        {/* Actions */}
        <div className="flex flex-col sm:flex-row justify-center gap-4 pb-12">
          <Button size="lg" variant="secondary" onClick={onBackToHome} className="gap-2">
            <Home className="h-4 w-4" />
            Back to Home
          </Button>
          <Button size="lg" variant="outline" className="gap-2">
            <TrendingUp className="h-4 w-4" />
            Download PDF Report
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;