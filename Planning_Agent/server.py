import json
from main import built_graph
from langgraph.graph import StateGraph
from flask import Flask, request, make_response,jsonify
from flask_cors import CORS
app = Flask(__name__)

CORS(app)

@app.route('/trial', methods=['POST', 'GET'])
def collector():
    if request.method == 'POST':
        json_data = request.data
        print(json_data)
        try_data = json.loads(json_data)
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

        result=built_graph.invoke({"input_data":user_data})

        ai_plan = result.get("formatted_output") or result.get("plan") or "No plan generated"

        print("\nAI PLAN GENERATED:\n", ai_plan)

        # --- Return the plan as JSON to frontend ---
        return jsonify({"plan": ai_plan})
if __name__ == "__main__":
    app.run(debug=True)
    
    


# #FOR TESTING PURPOSES ONLY: 

# from main import built_graph
# from langgraph.graph import StateGraph
# def collecctor():
#     user_data ={
#         "personal_info": {
#             "name": "Aryan Kumar",
#             "current_age": 30,
#             "gender": "Male",
#             "marital_status": "Married",
#             "number_of_children": 1
#         },
#         "financial_info": {
#             "income": {
#             "annual": 1200000
#             },
#             "expenses": {
#             "monthly_total": 55000,
#             "components": {
#                 "loan_emis": 20000,
#                 "investment_sips": 15000,
#                 "misc": 20000
#             }
#             },
#             "assets": {
#                 "savings": {
#                     "epf": 500000,
#                     "ppf": 200000,
#                     "nps": 150000,
#                     "bank_savings": 300000
#                 },
#                 "total_investments": 1000000,
#                 "portfolio_breakdown_percent": {
#                     "equity": 50,
#                     "mutual_funds": 20,
#                     "gold": 10,
#                     "crypto": 5,
#                     "other": 15
#                 },
#                 "emergency_fund": 250
#             },
#             "liabilities": {
#                 "total_debt": 500000,
#                 "monthly_debt_contribution": 20000
#             }
#         },
#         "goals": {
#             "short_term": [
#             {
#                 "name": "International Vacation",
#                 "target_amount": 300000
#             }
#             ],
#             "medium_term": [
#             {
#                 "name": "Buy a Car",
#                 "target_amount": 500000
#             }
#             ],
#             "long_term": [
#             {
#                 "name": "Child's Higher Education",
#                 "target_amount": 2500000
#             }
#             ]
#         },
#         "retirement_info": {
#             "desired_retirement_age": 60,
#             "retirement_lifestyle_description": "A comfortable life with travel twice a year and pursuing hobbies.",
#             "desired_retirement_expenses_inr": 75000,
#             "risk_tolerance_score": 10,
#             "investment_preferences": "Saving",
#             "annual_savings_rate_percent": 45677.78
#         }
#     }

#     result=built_graph.invoke({"input_data":user_data})
#     print(result)
# if __name__ == "__main__":
#     collecctor()