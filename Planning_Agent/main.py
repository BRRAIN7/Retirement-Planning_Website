from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from session_manager import insert
import numpy_financial as npf
from datetime import datetime
from feasibility import warnings_generator

from ML_models import get_goal_classification,risk_appetite_pred
from prompts import create_master_prompt

import ollama 


class AgentState(TypedDict):
    input_data:dict 
    risk_appetite : str 
    feasibility: dict
    plan:str
    formatted_output:str

    user_profile:dict
    goals: list[dict]
    retirement_plan:dict



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
        "retirement_info": input_data.get("retirement_info", {})
    }

    
    goals = input_data.get("goals", {})

    
    collected_goals = []
    for category, goals_list in goals.items():
        for g in goals_list:
            collected_goals.append({
                "term": category,  
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
    
    # We will loop through the goals and add the 'type' to each one
    updated_goals = []
    
    for goal in state["goals"]:
        # 1. Get the features the model needs
        # Your model expects 'goal_text', 'target_amount', 'goal_term'
        goal_text = goal["name"] 
        target_amount = goal["target_amount"]
        goal_term = goal["term"] # This comes from your input_collector
        
        # 2. Call the prediction function from MLmodels.py
        predicted_type = get_goal_classification(goal_text, target_amount, goal_term)
        
        # 3. Add the new 'type' to the goal dictionary
        goal['type'] = predicted_type
        updated_goals.append(goal)

    # 4. Save the enriched list back to the state
    state["goals"] = updated_goals
    
    print("Agent state after classification: ", state["goals"])
    return state


def risk_predictor(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Risk Predictor==========================")
    
    # 1. Build the data dictionary from the state.
    #    This pulls the 10 required features from the full user_profile.
    try:
        profile = state['user_profile']
        user_data = {
            'current_age': profile['age'],
            'number_of_children': profile['number_of_children'],
            'desired_retirement_age': profile['retirement_info']['desired_retirement_age'],
            'annual_income': profile['income']['annual'],
            'total_debt': profile['liabilities']['total_debt'],
            'emergency_fund': profile['assets']['emergency_fund'],
            'portfolio_percent_equity': profile['assets']['portfolio_breakdown_percent']['equity'],
            'portfolio_percent_crypto': profile['assets']['portfolio_breakdown_percent']['crypto'],
            'portfolio_percent_gold': profile['assets']['portfolio_breakdown_percent']['gold'],
            
            # Get the first short-term goal amount, or 0 if none
            'short_term_goal_amount': state['goals'][0]['target_amount'] if state['goals'] and state['goals'][0]['term'] == 'short_term' else 0
        }
    except KeyError as e:
        print(f"CRITICAL ERROR in risk_predictor: Missing key {e} in state.")
        print("Cannot calculate risk. Returning 'Medium' as default.")
        state["risk_appetite"] = "Medium"
        return state
    except Exception as e:
        print(f"CRITICAL ERROR formatting data for model: {e}")
        state["risk_appetite"] = "Medium"
        return state

    # 2. Call the prediction function WITH the data
    risk = risk_appetite_pred(user_data) # This now passes the data
    
    # 3. Store the result back into the state
    state["risk_appetite"] = risk
    print(f"Risk of the user is :{risk}")
    
    return state

def session_updater(state: AgentState) -> AgentState:
    print(" ")
    print("==========================Inside Session Updator==========================")
    insert(state)
    print (" ")
    return state

#SOME ASSUMPTIONS DONE FOR CALC SAKE IN financial_calc node
INFLATION_RATE = 0.06
INVESTMENT_RETURN_RATE = 0.12 # Assumed return for new investments
EPF_RETURN_RATE = 0.0825
PPF_RETURN_RATE = 0.071
NPS_RETURN_RATE = 0.10 # Assuming a moderate-risk NPS portfolio
def finantial_calc(state:AgentState) -> AgentState:
    print(" ")
    print("==========================Inside Financial Calculator==========================")


    #1. calc the monthly surplus --> monthlyincome - monthly expenses

    monthly_income=state["user_profile"]["income"]["annual"]/12
    state["user_profile"]["income"]["monthly_income"]=monthly_income

    monthly_surplus = state["user_profile"]["income"]["monthly_income"]-state["user_profile"]["expenses"]["monthly_total"]
    state["user_profile"]["monthly_surplus"]=monthly_surplus

    #2. Checking for emergency fund that i should have
        #emergency fund = essential monthly expenses * 3 or 6  (for 3 months or 6 months)
    
    essential_expenses= state["user_profile"]["expenses"]["monthly_total"]-state["user_profile"]["expenses"]["components"]["investment_sips"]

    target_emergency_fund=essential_expenses * 3 # kept a 3 month emergency fund for now
    emergency_fund_sip=0
    if state["user_profile"]["assets"]["emergency_fund"] < target_emergency_fund:
        shortfall=  target_emergency_fund - state["user_profile"]["assets"]["emergency_fund"]
        emergency_fund_sip = shortfall / 18
        dictionary= {
            "name":"Build Emergency Fund (very crucial)",
            "target_amount": shortfall,
            "term": "short_term",
            "type": "Savings",
            "required_monthly_investment": emergency_fund_sip 
        }

        state["goals"].append(dictionary)

    print(state)
    

    #3 Perform the Complete Retirement Calculation
    current_age = state["user_profile"]["age"]
    
    desired_retirement_age = state["user_profile"]["retirement_info"]["desired_retirement_age"]

    years_to_retirement = desired_retirement_age - current_age
    
    desired_monthly_expenses = state["user_profile"]["retirement_info"]["desired_retirement_expenses_inr"]
    current_annual_base_expense = desired_monthly_expenses * 12

    # a. Gross Corpus Calculation
    future_annual_expenses = npf.fv(INFLATION_RATE, years_to_retirement, 0, -current_annual_base_expense)
    gross_corpus = future_annual_expenses * 25 # Using the 4% rule (1/0.04 = 25)
    print(f"Years to Retirement: {years_to_retirement}")
    print(f"Future Annual Expenses (at retirement): ₹{future_annual_expenses:,.2f}")
    print(f"Gross Retirement Corpus Needed: ₹{gross_corpus:,.2f}")

    # b. Future Value of Existing Assets
    projected_future_assets = 0
    assets = state["user_profile"]["assets"]
    
    # Project EPF, PPF, NPS
    projected_future_assets += npf.fv(EPF_RETURN_RATE, years_to_retirement, 0, -assets["savings"]["epf"]) #investment emis are not considered 
    projected_future_assets += npf.fv(PPF_RETURN_RATE, years_to_retirement, 0, -assets["savings"]["ppf"]) #investment emis are not considered 
    projected_future_assets += npf.fv(NPS_RETURN_RATE, years_to_retirement, 0, -assets["savings"]["nps"]) #investment emis are not considered 
    
    # Assume 80% of other investments are for retirement
    retirement_investments_pv = assets["total_investments"] * 0.80
    projected_future_assets += npf.fv(INVESTMENT_RETURN_RATE, years_to_retirement, 0, -retirement_investments_pv)
    print(f"Projected Future Value of Existing Assets: ₹{projected_future_assets:,.2f}")
    
    # c. Net Corpus (The Shortfall)
    net_corpus_to_build = gross_corpus - projected_future_assets
    if net_corpus_to_build < 0:
        net_corpus_to_build = 0 
    print(f"Net Corpus (Shortfall) to Build: ₹{net_corpus_to_build:,.2f}") # Check for unrealistic maybe??

    # d. Required SIP to cover the shortfall
    required_retirement_sip = 0
    if net_corpus_to_build > 0:
        # Using numpy_financial.pmt to calculate the monthly payment
        required_retirement_sip = npf.pmt(
            rate=INVESTMENT_RETURN_RATE / 12, 
            nper=years_to_retirement * 12, 
            pv=0, 
            fv=-net_corpus_to_build
        )
    print(f"Required Monthly SIP for Retirement: ₹{required_retirement_sip:,.2f}")
    
    # Store the results back into the state for later nodes
    state["retirement_plan"] = {
        "years_to_retirement": years_to_retirement,
        "gross_corpus": gross_corpus,
        "projected_future_assets": projected_future_assets,
        "net_corpus_to_build": net_corpus_to_build,
        "required_sip": required_retirement_sip
    }


    #4. Calculate the True "Remaining Surplus"
    print("\n--- Calculating Remaining Surplus for Other Goals ---")
    
  
    remaining_surplus = state["user_profile"]["monthly_surplus"]
    
 
    remaining_surplus -= state["retirement_plan"]["required_sip"]
    remaining_surplus -= emergency_fund_sip
    

    state["user_profile"]["remaining_surplus"] = remaining_surplus
    print(f"True Remaining Surplus for other goals: ₹{remaining_surplus:,.2f}")

    # 5. Process All Other User Goals
    print("\n--- Processing Other User Goals ---")
    
    LOAN_INTEREST_RATE = 0.09 

    for goal in state["goals"]:
        if "Build Emergency Fund (very crucial)" in goal["name"]:
            continue
        #CHANGE THIS IF NEEDED
        if "time_horizon_years" not in goal:
            if goal["term"] == "short_term":
                goal["time_horizon_years"] = 2
            elif goal["term"] == "medium_term":
                goal["time_horizon_years"] = 5
            else: # long_term
                goal["time_horizon_years"] = 10 

        inflation_adj_future_cost = npf.fv(
            rate=INFLATION_RATE, 
            nper=goal["time_horizon_years"], 
            pmt=0, 
            pv=-goal["target_amount"]
        )
        goal["inflation_adjusted_cost"] = inflation_adj_future_cost
        
        if goal["type"] == "Loan-Assisted":
            down_payment_needed = inflation_adj_future_cost * 0.20
            loan_principal_amount = inflation_adj_future_cost * 0.80
            
            # b. Calculate the EMI for the loan portion
            estimated_emi = npf.pmt(
                rate=LOAN_INTEREST_RATE / 12,
                nper=goal["time_horizon_years"] * 12,
                pv=-loan_principal_amount
            )
            
            goal["down_payment_needed"] = down_payment_needed
            goal["estimated_emi"] = abs(estimated_emi) 
            

        elif goal["type"] in ["Investment", "Savings"]:
            required_sip = 0
            if inflation_adj_future_cost > 0:
                 required_sip = npf.pmt(
                     rate=INVESTMENT_RETURN_RATE / 12,
                     nper=goal["time_horizon_years"] * 12,
                     pv=0,
                     fv=-inflation_adj_future_cost
                 )
            
            goal["required_monthly_investment"] = abs(required_sip)


    return state

def feasibility_checker(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Feasibility checker==========================")
    feasibility_report = warnings_generator(state)
    state['feasibility'] = feasibility_report
    return state

def plan_generator(state:AgentState) ->AgentState :
    ###################################   Hardcoded for testing   ########################################################
    state["feasibility"]={
        "Build Emergency Fund (very crucial)": {
            "status": "Healthy_&_Achievable"
        },
        "International Vacation": {
            "status": "Unrealistic",
            "warning": "This goal is not affordable with your current remaining surplus."
        },
        "Buy a Car": {
            "status": "Unrealistic",
            "warning": "This goal is not affordable with your current remaining surplus."
        },
        "Child's Higher Education": {
            "status": "Unrealistic",
            "warning": "This goal is not affordable with your current remaining surplus."
        }
    }
    #################################################################################################

    print(" ")
    print("==========================Inside Plan generator==========================")

    # final_prompt= create_master_prompt(state)
    # result= ollama.chat(
    #     model="phi3:mini",
    #     messages=[{ "role":"user" ,"content" :final_prompt }],
    #     stream=True
    # )

    # for i in result:
    #     print(i["message"]["content"], end="", flush=True)
    

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




