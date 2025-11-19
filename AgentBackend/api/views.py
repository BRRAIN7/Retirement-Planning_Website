import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# This import works because of Step 3!
from Planning_Agent.main import built_graph

# --- NEW: User Registration View ---
@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"error": "Username and password required"}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)
            
            # Create the new user
            user = User.objects.create_user(username=username, password=password)
            return JsonResponse({"success": f"User '{username}' created"}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

# --- NEW: User Login View ---
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"error": "Username and password required"}, status=400)

            # Check credentials
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)  # This creates the session
                return JsonResponse({"success": f"Welcome, {username}!"})
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=401)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


# --- YOUR MIGRATED FLASK CODE ---
# @login_required protects this endpoint. Only logged-in users can access it.
@login_required
@csrf_exempt
def collector_view(request):
    if request.method == 'POST':
        json_data = request.body
        print(json_data)
        
        try_data = json.loads(json_data)
        
        # --- This is your EXACT logic from Flask ---
        user_data = {
            "personal_info": {
                "name": try_data["personal_info"]["name"],
                "current_age": int(try_data["personal_info"]["current_age"]),
                "gender": try_data["personal_info"]["gender"],
                "marital_status": try_data["personal_info"]["marital_status"],
                "number_of_children": int(try_data["personal_info"]["number_of_children"])
            },
            "financial_info": {
                "income": {
                    "annual": int(try_data["financial_info"]["income"]["annual"])
                },
                "expenses": {
                    "monthly_total": int(try_data["financial_info"]["expenses"]["monthly_total"]),
                    "components": {
                        "loan_emis": int(try_data["financial_info"]["expenses"]["components"]["loan_emis"]),
                        "investment_sips": int(try_data["financial_info"]["expenses"]["components"]["investment_sips"]),
                        "misc": int(try_data["financial_info"]["expenses"]["components"]["misc"])
                    }
                },
                "assets": {
                    "savings": {
                        "epf": int(try_data["financial_info"]["assets"]["savings"]["epf"]),
                        "ppf": int(try_data["financial_info"]["assets"]["savings"]["ppf"]),
                        "nps": int(try_data["financial_info"]["assets"]["savings"]["nps"]),
                        "bank_savings": int(try_data["financial_info"]["assets"]["savings"]["bank_savings"])
                    },
                    "total_investments": int(try_data["financial_info"]["assets"]["total_investments"]),
                    "portfolio_breakdown_percent": {
                        "equity": int(try_data["financial_info"]["assets"]["portfolio_breakdown_percent"]["equity"]),
                        "mutual_funds": int(try_data["financial_info"]["assets"]["portfolio_breakdown_percent"]["mutual_funds"]),
                        "gold": int(try_data["financial_info"]["assets"]["portfolio_breakdown_percent"]["gold"]),
                        "crypto": int(try_data["financial_info"]["assets"]["portfolio_breakdown_percent"]["crypto"]),
                        "other": int(try_data["financial_info"]["assets"]["portfolio_breakdown_percent"]["other"])
                    },
                    "emergency_fund": int(try_data["financial_info"]["assets"]["emergency_fund"])
                },
                "liabilities": {
                    "total_debt": int(try_data["financial_info"]["liabilities"]["total_debt"]),
                    "monthly_debt_contribution": int(try_data["financial_info"]["liabilities"]["monthly_debt_contribution"])
                }
            },
            "goals": {
                "short_term": [
                    {
                        "name": goal["name"],
                        "target_amount": int(goal["target_amount"])
                    } for goal in try_data["goals"]["short_term"]
                ],
                "medium_term": [
                    {
                        "name": goal["name"],
                        "target_amount": int(goal["target_amount"])
                    } for goal in try_data["goals"]["medium_term"]
                ],
                "long_term": [
                    {
                        "name": goal["name"],
                        "target_amount": int(goal["target_amount"])
                    } for goal in try_data["goals"]["long_term"]
                ]
            },
            "retirement_info": {
                "desired_retirement_age": int(try_data["retirement_info"]["desired_retirement_age"]),
                "retirement_lifestyle_description": try_data["retirement_info"]["retirement_lifestyle_description"],
                "desired_retirement_expenses_inr": int(try_data["retirement_info"]["desired_retirement_expenses_inr"]),
                "risk_tolerance_score": int(try_data["retirement_info"]["risk_tolerance_score"]),
                "investment_preferences": try_data["retirement_info"]["investment_preferences"],
                "annual_savings_rate_percent": float(try_data["retirement_info"]["annual_savings_rate_percent"])
            }
        }

        # --- This is also your EXACT logic from Flask ---
        result = built_graph.invoke({"input_data": user_data})
        ai_plan = result.get("formatted_output") or result.get("plan") or "No plan generated"
        print("\nAI PLAN GENERATED:\n", ai_plan)

        # --- The return is now a JsonResponse ---
        return JsonResponse({"plan": ai_plan})
    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
