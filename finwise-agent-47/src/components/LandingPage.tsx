import { Button } from "@/components/ui/button";
import { ArrowRight, Brain, TrendingUp, Shield, Sparkles } from "lucide-react";

const LandingPage = ({ onGetStarted }: { onGetStarted: () => void }) => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-accent/5 to-background">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMwMDAiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItaDJWMzRoLTJ6bTAtNGgydjJoLTJ2LTJ6bS0yIDJ2Mmgydi0yaC0yem0wLTJ2Mmgydi0yaC0yem0wLTJoMnYyaC0ydi0yem0yLTJ2Mmgydi0yaC0yem0wLTJ2Mmgydi0yaC0yem0wLTJ2Mmgydi0yaC0yem0wLTJ2Mmgydi0yaC0yem0tMiAwaDJ2MmgtMnYtMnptMC0yaDJ2MmgtMnYtMnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-40"></div>

        <div className="container relative mx-auto px-6 py-24 lg:py-32">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary">
              <Sparkles className="h-4 w-4" />
              AI-Powered Financial Intelligence
            </div>

            <h1 className="mb-6 text-5xl font-bold leading-tight tracking-tight text-foreground lg:text-6xl">
              Your Personal
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                {" "}
                AI Financial{" "}
              </span>
              Advisor
            </h1>

            <p className="mb-10 text-xl text-muted-foreground lg:text-2xl">
              Smart financial planning powered by machine learning. Get
              personalized insights, retirement planning, and investment advice
              tailored to your unique goals.
            </p>

            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button
                size="lg"
                onClick={onGetStarted}
                className="group h-14 gap-2 px-8 text-lg shadow-lg hover:shadow-glow transition-all"
              >
                Get Started Free
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
              <Button size="lg" variant="outline" className="h-14 px-8 text-lg">
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-background py-24">
        <div className="container mx-auto px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-foreground">
              Intelligent Financial Planning
            </h2>
            <p className="text-lg text-muted-foreground">
              Advanced AI technology to help you achieve your financial goals
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <div className="group rounded-2xl border border-border bg-card p-8 transition-all hover:shadow-lg hover:border-primary/50">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <Brain className="h-7 w-7" />
              </div>
              <h3 className="mb-3 text-xl font-semibold text-card-foreground">
                AI-Powered Insights
              </h3>
              <p className="text-muted-foreground">
                Machine learning algorithms analyze your financial data to
                provide personalized recommendations and predictions.
              </p>
            </div>

            <div className="group rounded-2xl border border-border bg-card p-8 transition-all hover:shadow-lg hover:border-primary/50">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-secondary/10 text-secondary group-hover:bg-secondary group-hover:text-secondary-foreground transition-colors">
                <TrendingUp className="h-7 w-7" />
              </div>
              <h3 className="mb-3 text-xl font-semibold text-card-foreground">
                Goal-Based Planning
              </h3>
              <p className="text-muted-foreground">
                Set short-term and long-term financial goals. Our AI helps you
                create actionable plans to achieve them faster.
              </p>
            </div>

            <div className="group rounded-2xl border border-border bg-card p-8 transition-all hover:shadow-lg hover:border-primary/50">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-accent/10 text-accent group-hover:bg-accent group-hover:text-accent-foreground transition-colors">
                <Shield className="h-7 w-7" />
              </div>
              <h3 className="mb-3 text-xl font-semibold text-card-foreground">
                Risk Assessment
              </h3>
              <p className="text-muted-foreground">
                Understand your risk tolerance and get investment strategies
                that match your comfort level and financial objectives.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
