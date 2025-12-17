import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { Send, Bot, User, Sparkles, FileText, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "./api";

const ChatPage = ({
  userData,
  onStartAssessment,
}: {
  userData: any;
  onStartAssessment: () => void;
}) => {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: `Hi ${
        userData?.name || "there"
      }! I'm your AI financial advisor. I can help answer questions about your finances, investments, and retirement planning. How can I assist you today?`,
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await api.post("/chat/", {
        message: userMessage, // Django expects this key
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.data.reply }, // Django returns reply
      ]);
    } catch (error) {
      console.warn("Chat backend failed:", error);

      const mockResponse = generateMockResponse(userMessage);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: mockResponse },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockResponse = (query: string) => {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes("retire") || lowerQuery.includes("retirement")) {
      return "Based on your current financial situation, I'd recommend starting to plan for retirement now. Would you like to complete a full financial assessment?";
    }

    if (lowerQuery.includes("invest") || lowerQuery.includes("investment")) {
      return "Investment strategies depend on your risk tolerance, financial goals, and time horizon. I recommend completing our comprehensive assessment. Would you like to proceed?";
    }

    if (lowerQuery.includes("save") || lowerQuery.includes("savings")) {
      return `With a monthly income of ₹${
        userData?.monthlyIncome || 0
      } and expenses of ₹${
        userData?.monthlyExpenses || 0
      }, you have a potential monthly savings of ₹${
        (userData?.monthlyIncome || 0) - (userData?.monthlyExpenses || 0)
      }. I can help you optimize this further with a detailed assessment.`;
    }

    return "That's an interesting question! To give you personalized financial advice, I'd recommend completing our full financial assessment.";
  };

  // 🚪 Logout handler
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    toast.success("Logged out successfully!");
    navigate("/auth");
  };

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <div className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/30">
        <div className="container mx-auto flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              <Bot className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">AI Financial Advisor</h1>
              <p className="text-sm text-muted-foreground">
                Always here to help
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={onStartAssessment}
              className="gap-2"
              variant="default"
            >
              <FileText className="h-4 w-4" />
              Full Assessment
            </Button>

            {/* 🚪 Logout Button */}
            <Button
              variant="destructive"
              className="gap-2"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 px-4 py-6" ref={scrollRef}>
        <div className="container mx-auto max-w-3xl space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.role === "assistant" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
              )}

              <Card
                className={`max-w-[80%] p-4 ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card"
                }`}
              >
                <p className="text-sm leading-relaxed">{message.content}</p>
              </Card>

              {message.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/10">
                  <User className="h-4 w-4 text-accent" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <Sparkles className="h-4 w-4 animate-pulse text-primary" />
              </div>
              <Card className="p-4">
                <div className="flex gap-1">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/30">
        <div className="container mx-auto max-w-3xl px-4 py-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) =>
                e.key === "Enter" && !isLoading && handleSend()
              }
              placeholder="Ask about your finances, investments, retirement..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              size="icon"
              className="h-10 w-10 shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
