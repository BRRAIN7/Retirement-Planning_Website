from main import built_graph
from langgraph.graph import StateGraph

def collecctor():
    user_data ={
        "personal_info": {
            "name": "Arnav Kumar",
            "age": 30,
            "gender": "Male",
            "marital_status": "Married",
            "number_of_children": 1
        },
        "financial_info": {
            "income": {
            "annual": 1200000
            },
            "expenses": {
            "monthly_total": 55000,
            "components": {
                "loan_emis": 20000,
                "investment_sips": 15000,
                "misc": 20000
            }
            },
            "assets": {
            "savings": {
                "epf": 500000,
                "ppf": 200000,
                "nps": 150000,
                "bank_savings": 300000
            },
            "total_investments": 1000000,
            "portfolio_breakdown_percent": {
                "equity": 50,
                "mutual_funds": 20,
                "gold": 10,
                "crypto": 5,
                "other": 15
            },
            "emergency_fund": 250000
            },
            "liabilities": {
            "total_debt": 500000,
            "monthly_debt_contribution": 20000
            }
        },
        "goals": {
            "short_term": [
            {
                "name": "International Vacation",
                "target_amount": 300000
            }
            ],
            "medium_term": [
            {
                "name": "Buy a Car",
                "target_amount": 500000
            }
            ],
            "long_term": [
            {
                "name": "Child's Higher Education",
                "target_amount": 2500000
            }
            ]
        },
        "retirement_info": {
            "desired_age": 60,
            "expected_lifestyle_description": "A comfortable life with travel twice a year and pursuing hobbies.",
            "expected_monthly_expenses": 75000
        }
    }

    result=built_graph.invoke({"input_data":user_data})
    print(result)
if __name__ == "__main__":
    collecctor()