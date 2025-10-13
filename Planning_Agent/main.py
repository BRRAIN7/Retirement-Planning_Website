from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from session_manager import insert


from ML_models import goal_classification,risk_appetite_pred


class AgentState(TypedDict):
    input_data:dict 
    risk_appetite : str 
    feasibility: dict
    plan:str
    formatted_output:str

    user_profile:dict
    goals: list[dict]



def input_collector(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Input Collector==========================")
    input_data = state.get("input_data", {})

    
    user_profile = {
        "name": input_data.get("personal_info", {}).get("name"),
        "age": input_data.get("personal_info", {}).get("current_age"),
        "gender": input_data.get("personal_info", {}).get("gender"),
        "marital_status": input_data.get("personal_info", {}).get("marital_status"),
        "number_of_children": input_data.get("personal_info", {}).get("number_of_children"),
        "income": input_data.get("financial_info", {}).get("income", {}),
        "expenses": input_data.get("financial_info", {}).get("expenses", {}),
        "assets": input_data.get("financial_info", {}).get("assets", {}),
        "liabilities": input_data.get("financial_info", {}).get("liabilities", {}),
    }

    
    goals = input_data.get("goals", {})

    
    collected_goals = []
    for category, goals_list in goals.items():
        for g in goals_list:
            collected_goals.append({
                "category": category,  
                "name": g.get("name"),
                "target_amount": g.get("target_amount")
            })

   
    state["user_profile"] = user_profile
    state["goals"] = collected_goals

    print("User Profile extracted:", user_profile)
    print(" ")
    print("Goals Extracted(before classification) ",state["goals"])
   
    return state

def goal_classifier(state: AgentState)->AgentState:
    print(" ")
    print("==========================Inside Goal Classifier ==========================")
    state["goals"]=goal_classification(state)
    
    print("Agent state after classificatino:  ",state["goals"])
    return state


def risk_predictor(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Risk Predictor==========================")    
    risk= risk_appetite_pred()
    state["risk_appetite"]=risk
    print(f"Risk of the user is :{risk}")
    return state


def session_updater(state: AgentState) -> AgentState:
    print(" ")
    print("==========================Inside Session Updator==========================")
    insert(state)
    print (" ")
    return state


def finantial_calc(state:AgentState) -> AgentState:
    print(" ")
    print("==========================Inside Finantial Calculator==========================")


    #1. calc the monthly surplus --> monthlyincome - monthly expenses

    monthly_income=state["user_profile"]["income"]["annual"]/12
    state["user_profile"]["income"]["monthly_income"]=monthly_income

    monthly_surplus = state["user_profile"]["income"]["monthly_income"]-state["user_profile"]["expenses"]["monthly_total"]
    state["user_profile"]["monthly_surplus"]=monthly_surplus

    #2. Checking for emergency fund that i should have
        #emergency fund = essential monthly expenses * 3 or 6  (for 3 months or 6 months)
    
    essential_expenses= state["user_profile"]["expenses"]["monthly_total"]-state["user_profile"]["expenses"]["components"]["investment_sips"]

    target_emergency_fund=essential_expenses * 3 # kept a 3 month emergency fund for now

    if (target_emergency_fund < state["user_profile"]["assets"]["emergency_fund"]):
        dictionary= {
            "name":"Build Emergency Fund (very crucial)",
            "target_amount": state["user_profile"]["assets"]["emergency_fund"]-target_emergency_fund,
            "term": "short_term",
            "type": "Savings"        
        }

        state["goals"].append(dictionary)

    print(state)
    







    return state

def feasibility_checker(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Feasibility checker==========================")
    return state

def plan_generator(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Plan generator==========================")
    return state

def output(state:AgentState)-> AgentState:
    print(" ")
    print("Displays the output")
    return state


graph = StateGraph(AgentState)
graph.add_node("input_collector",input_collector)
graph.add_node("goal_classifier",goal_classifier)
graph.add_node("session_updater",session_updater)
graph.add_node("risk_predictor",risk_predictor)
graph.add_node("finantial_calc",finantial_calc)
graph.add_node("feasibility_checker",feasibility_checker)
graph.add_node("plan_generator",plan_generator)
graph.add_node("output",output)

graph.add_edge(START,"input_collector")
graph.add_edge("input_collector","goal_classifier")
graph.add_edge("goal_classifier","risk_predictor")
graph.add_edge("risk_predictor","session_updater")
graph.add_edge("session_updater","finantial_calc")
graph.add_edge("finantial_calc","feasibility_checker")
graph.add_edge("feasibility_checker","plan_generator")
graph.add_edge("plan_generator","output")
graph.add_edge("output",END)

built_graph= graph.compile()




