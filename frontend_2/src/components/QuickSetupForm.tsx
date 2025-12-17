import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

const QuickSetupForm = ({ onComplete }: { onComplete: (data: any) => void }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    monthlyIncome: "",
    monthlyExpenses: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.age || !formData.monthlyIncome || !formData.monthlyExpenses) {
      toast.error("Please fill in all fields");
      return;
    }

    if (Number(formData.age) < 18 || Number(formData.age) > 100) {
      toast.error("Please enter a valid age between 18 and 100");
      return;
    }

    if (Number(formData.monthlyIncome) <= 0 || Number(formData.monthlyExpenses) < 0) {
      toast.error("Please enter valid income and expense amounts");
      return;
    }

    setIsLoading(true);
    
    setTimeout(() => {
      onComplete({
        ...formData,
        age: Number(formData.age),
        monthlyIncome: Number(formData.monthlyIncome),
        monthlyExpenses: Number(formData.monthlyExpenses),
      });
      toast.success("Profile created successfully!");
      setIsLoading(false);
    }, 1000);
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-primary/5 to-accent/5 px-4 py-12">
      <Card className="w-full max-w-lg shadow-xl">
        <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-bold">Quick Setup</CardTitle>
          <CardDescription className="text-base">
            Let's start with some basic information about your finances
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                placeholder="Enter your full name"
                value={formData.name}
                onChange={(e) => handleChange("name", e.target.value)}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                placeholder="Enter your age"
                value={formData.age}
                onChange={(e) => handleChange("age", e.target.value)}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="income">Monthly Income (₹)</Label>
              <Input
                id="income"
                type="number"
                placeholder="Enter your monthly income"
                value={formData.monthlyIncome}
                onChange={(e) => handleChange("monthlyIncome", e.target.value)}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="expenses">Monthly Expenses (₹)</Label>
              <Input
                id="expenses"
                type="number"
                placeholder="Enter your monthly expenses"
                value={formData.monthlyExpenses}
                onChange={(e) => handleChange("monthlyExpenses", e.target.value)}
                disabled={isLoading}
              />
            </div>

            <Button
              type="submit"
              className="w-full h-12 text-base"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Setting up your profile...
                </>
              ) : (
                "Continue to Chat"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuickSetupForm;
