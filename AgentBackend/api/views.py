from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .auth import UnsafeSessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
import decimal
# Import your models
from .models import (
    UserProfile, Income, Expenses, Assets, Liabilities,
    Goal, MessageHistory, RetirementInfo
)

# Import the new Serializer
from .serializers import FinancialInputSerializer

# Import your LangGraph agent
from Planning_Agent.main import built_graph 

# ==========================================
# HELPER FUNCTIONS (Context Management)
# ==========================================

MAX_HISTORY = 10
def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj

def save_message(user, role: str, content: str):
    """Saves a message to history and enforces the limit."""
    MessageHistory.objects.create(user=user, role=role, content=content)

    # Keep only last MAX_HISTORY messages to save DB space/tokens
    qs = MessageHistory.objects.filter(user=user).order_by("-timestamp")
    if qs.count() > MAX_HISTORY:
        to_delete = qs[MAX_HISTORY:]
        # Extract IDs to delete specific rows
        MessageHistory.objects.filter(id__in=[m.id for m in to_delete]).delete()

def load_messages(user, limit: int = 10):
    """Loads chat history formatted for the AI."""
    qs = MessageHistory.objects.filter(user=user).order_by("-timestamp")[:limit]
    msgs = list(qs)[::-1]  # Reverse to get Oldest -> Newest
    return [{"role": m.role, "content": m.content} for m in msgs]

def clear_messages(user):
    """Clears history when a new plan is generated."""
    MessageHistory.objects.filter(user=user).delete()

def build_state_from_db(user):
    """
    Reconstructs the State dictionary from the Database 
    to feed into the LangGraph Agent.
    """
    # Using OneToOne relationships (related_name) is safer and cleaner
    try:
        profile = user.profile
        income = user.income
        assets = user.assets
        liabilities = user.liabilities
        expenses = user.expenses
        retirement = user.retirement_info
    except ObjectDoesNotExist:
        # If any core component is missing, we can't build state
        raise ValueError("User financial data is incomplete.")

    goals_qs = Goal.objects.filter(user=user)
    goals_list = []
    for g in goals_qs:
        goals_list.append({
            "name": g.name,
            "term": g.term,
            "target_amount": float(g.target_amount or 0),
            "type": g.type,
        })

    messages = load_messages(user)

    state = {
        "input_data": {},   # Not needed for chat, we rely on the DB state below
        "risk_appetite": getattr(profile, 'risk_appetite', "") or "", # Fallback if field removed
        "feasibility": {},
        "plan": "",
        "formatted_output": "",

        "user_profile": {
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "marital_status": profile.marital_status,
            "number_of_children": profile.number_of_children,
            "income": {
                "annual": float(income.annual_income or 0),
            },
            "expenses": {
                "monthly_total": float(expenses.monthly_total or 0),
                "components": {
                    "loan_emis": float(expenses.loan_emis or 0),
                    "investment_sips": float(expenses.investment_sips or 0),
                    "misc": float(expenses.misc or 0),
                },
            },
            "assets": {
                "savings": {
                    "epf": float(assets.epf or 0),
                    "ppf": float(assets.ppf or 0),
                    "nps": float(assets.nps or 0),
                    "bank_savings": float(assets.bank_savings or 0),
                },
                "total_investments": float(assets.total_investments or 0),
                "portfolio_breakdown_percent": {
                    "equity": float(assets.equity_percent or 0),
                    "mutual_funds": float(assets.mutual_funds_percent or 0),
                    "gold": float(assets.gold_percent or 0),
                    "crypto": float(assets.crypto_percent or 0),
                    "other": float(assets.other_percent or 0),
                },
                "emergency_fund": float(assets.emergency_fund or 0),
            },
            "liabilities": {
                "total_debt": float(liabilities.total_debt or 0),
                "monthly_debt_contribution": float(liabilities.monthly_debt_contribution or 0),
            },
            "retirement_info": {
                "desired_retirement_age": retirement.desired_retirement_age,
                "retirement_lifestyle_description": retirement.retirement_lifestyle_description,
                "desired_retirement_expenses_inr": float(retirement.desired_retirement_expenses_inr or 0),
                "risk_tolerance_score": retirement.risk_tolerance_score,
                "investment_preferences": retirement.investment_preferences,
                "annual_savings_rate_percent": float(retirement.annual_savings_rate_percent or 0),
            },
        },

        "goals": goals_list,
        "retirement_plan": {},
        "messages": messages,
    }

    return state


# ==========================================
# 1. AUTH VIEWS
# ==========================================

from rest_framework.authtoken.models import Token

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "newUser": True
            },
            status=201
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "newUser": False
            },
            status=200
        )


# ==========================================
# 2. SUBMIT DATA & GENERATE PLAN
# ==========================================

class SubmitFinancialDataView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(">>> SubmitFinancialDataView HIT")
        print("\n===== RAW JSON RECEIVED BY BACKEND =====")
        print(request.data)
        print("========================================\n")
        user = request.user
        
        # --- 1. Validate & Clean Data with Serializer ---
        # This replaces all the manual dictionary extraction logic
        serializer = FinancialInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            print("\n===== VALIDATION ERRORS =====")
            print(serializer.errors)
            print("================================\n")
            return Response(
                {"error": "Validation failed", "details": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- 2. Save to Database ---
        # Using the custom save_data method we defined in serializers.py
        try:
            serializer.save_data(user=user)
        except Exception as e:
            return Response(
                {"error": f"Database error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # --- 3. Prepare AI Context ---
        # Clear old chat history since this is a fresh plan
        clear_messages(user)

        # Construct State for LangGraph
        # We pass "input_data" directly from the serializer for the 'new_user' path
        state = {
            "input_data": serializer.validated_data, 
            "risk_appetite": "",
            "feasibility": {},
            "plan": "",
            "formatted_output": "",
            "user_profile": {},    # Populated by the graph based on input_data
            "goals": [],
            "retirement_plan": {},
            "messages": [],        # Empty -> triggers "new_user" logic in graph
        }

        # --- 4. Invoke AI Agent ---
        try:
            state = convert_decimals(state)
            result = built_graph.invoke(state)
            print("\n======== RAW AGENT RESULT ========")
            print(result)
            print("==================================\n")
        except Exception as e:
            return Response(
                {"error": f"AI Agent Error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # --- 5. Process Result ---
        plan = (
            result.get("formatted_output")
            or result.get("plan")
            or "No plan generated by the AI."
        )

        # Update Risk Appetite if AI calculated it
        new_risk = result.get("risk_appetite")
        # Check if profile exists before updating (it should, thanks to save_data)
        if new_risk and hasattr(user, 'profile'):
            user.profile.risk_appetite = new_risk # Assuming you added this field back or use a dedicated model
            # If you removed risk_appetite from UserProfile as suggested, 
            # you might ignore this or update RetirementInfo instead.
            # user.retirement_info.risk_tolerance_score = ... (if mapping string to int)
            user.profile.save()

        # Save the Plan as the first assistant message
        save_message(user, "assistant", plan)

        
        retirement_plan = result.get("retirement_plan", {})
        user_profile = result.get("user_profile", {})

        response_payload = {
            "plan": plan,

            "metrics": {
                "years_to_retirement": retirement_plan.get("years_to_retirement"),
                "monthly_surplus": float(user_profile.get("monthly_surplus", 0)),
                "required_retirement_sip": float(retirement_plan.get("required_sip", 0)),
                "gross_retirement_corpus": float(retirement_plan.get("gross_corpus", 0)),
                "projected_future_assets": float(retirement_plan.get("projected_future_assets", 0)),
                "net_corpus_to_build": float(retirement_plan.get("net_corpus_to_build", 0)),
            },

            "goals": result.get("goals", []),
            "feasibility": result.get("feasibility", {}),
        }

        return Response(response_payload, status=status.HTTP_200_OK)


# ==========================================
# 3. CHAT INTERFACE (Follow-up Questions)
# ==========================================

class ChatView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        message = request.data.get("message")

        if not message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- 1. Rebuild Context from DB ---
        try:
            state = build_state_from_db(user)
        except ValueError as e:
            return Response(
                {"error": "No financial plan found. Please submit data first."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": "Failed to load user context."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # --- 2. Update State with New Message ---
        user_msg = {"role": "user", "content": message}
        
        # Ensure 'messages' key exists in state
        if "messages" not in state:
            state["messages"] = []
            
        state["messages"].append(user_msg)
        save_message(user, "user", message)

        # --- 3. Invoke AI Agent ---
        # The agent will see existing history + new message -> "modify" or "chat" path
        try:
            state = convert_decimals(state)
            result = built_graph.invoke(state)
        except Exception as e:
            return Response(
                {"error": "AI Agent failed to respond."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # --- 4. Process Response ---
        reply = result.get("formatted_output") or result.get("plan")
        if not reply:
            reply = "I processed your message but couldn't generate a specific response."

        save_message(user, "assistant", reply)

        # Optional: If chat caused a risk profile update
        new_risk = result.get("risk_appetite")
        if new_risk and hasattr(user, 'profile'):
             # Logic to update risk if needed
             pass

        return Response({"reply": reply}, status=status.HTTP_200_OK)
    
class VerifyTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"valid": True}, status=200)