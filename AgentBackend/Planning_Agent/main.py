from typing import TypedDict, Literal
from langgraph.graph import StateGraph,END
from .session_manager import insert
import numpy_financial as npf
from datetime import datetime
from .feasibility import warnings_generator
import json
from .ML_models import get_goal_classification,risk_appetite_pred
from .prompts import create_master_prompt,get_general_chat_prompt

import os
from groq import Groq
from dotenv import load_dotenv

class AgentState(TypedDict, total=False):
    input_data:dict
    risk_appetite : str
    feasibility: dict
    plan:str
    formatted_output:str

    user_profile:dict
    goals: list[dict]
    retirement_plan:dict
    messages:list
    solvency_status:str
    solvency_gap:float



def input_collector(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Input Collector==========================")
    input_data = state.get("input_data", {})


    user_profile = {
        "name": input_data.get("personal_info", {}).get("name"),
        "age": input_data.get("personal_info", {}).get("current_age"),
        "gender": input_data.get("personal_info", {}).get("gender"),
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
    #insert(state)
    print (" ")
    return state

#SOME ASSUMPTIONS DONE FOR CALC SAKE IN financial_calc node
INFLATION_RATE = 0.06
INVESTMENT_RETURN_RATE = 0.12 # Assumed return for new investments
EPF_RETURN_RATE = 0.0825
PPF_RETURN_RATE = 0.071
NPS_RETURN_RATE = 0.10 # Assuming a moderate-risk NPS portfolio
from datetime import datetime
import numpy_financial as npf



def finantial_calc(state: "AgentState") -> "AgentState":
    print(" ")
    print("==========================Inside Financial Calculator==========================")

    # 1. SETUP & SURPLUS
    monthly_income = state["user_profile"]["income"]["annual"] / 12
    state["user_profile"]["income"]["monthly_income"] = monthly_income
    
    monthly_surplus = state["user_profile"]["income"]["monthly_income"] - state["user_profile"]["expenses"]["monthly_total"]
    state["user_profile"]["monthly_surplus"] = monthly_surplus

    # 2. RETIREMENT CALCULATION
    current_age = state["user_profile"]["age"]
    desired_retirement_age = state["user_profile"]["retirement_info"]["desired_retirement_age"]
    years_to_retirement = desired_retirement_age - current_age
    retirement_year = int(datetime.now().year + years_to_retirement)
    
    # Fallback Logic: If 0 input, assume they want to maintain current lifestyle
    desired_monthly_expenses_input = float(state["user_profile"]["retirement_info"].get("desired_retirement_expenses_inr", 0))
    if desired_monthly_expenses_input <= 0:
        base_monthly_expense = state["user_profile"]["expenses"]["monthly_total"]
    else:
        base_monthly_expense = desired_monthly_expenses_input

    current_annual_base_expense = base_monthly_expense * 12

    # Gross Corpus (Inflated)
    future_annual_expenses = npf.fv(INFLATION_RATE, years_to_retirement, 0, -current_annual_base_expense)
    gross_corpus = future_annual_expenses * 25 

    # Assets & Net Corpus
    projected_future_assets = 0
    assets = state["user_profile"]["assets"]
    projected_future_assets += npf.fv(EPF_RETURN_RATE, years_to_retirement, 0, -assets["savings"]["epf"]) 
    projected_future_assets += npf.fv(PPF_RETURN_RATE, years_to_retirement, 0, -assets["savings"]["ppf"]) 
    projected_future_assets += npf.fv(NPS_RETURN_RATE, years_to_retirement, 0, -assets["savings"]["nps"]) 
    retirement_investments_pv = assets["total_investments"] * 0.80
    projected_future_assets += npf.fv(INVESTMENT_RETURN_RATE, years_to_retirement, 0, -retirement_investments_pv)
    
    net_corpus_to_build = gross_corpus - projected_future_assets
    if net_corpus_to_build < 0: net_corpus_to_build = 0 

    required_retirement_sip = 0
    if net_corpus_to_build > 0:
        required_retirement_sip = npf.pmt(
            rate=INVESTMENT_RETURN_RATE / 12, 
            nper=years_to_retirement * 12, 
            pv=0, 
            fv=-net_corpus_to_build
        )
    
    state["retirement_plan"] = {
        "required_sip": abs(required_retirement_sip),
        "gross_corpus": gross_corpus,
        "net_corpus_to_build": net_corpus_to_build,
        "retirement_year": retirement_year,
        "years_to_retirement": years_to_retirement,
        "projected_future_assets": projected_future_assets,
        "existing_assets_value": assets["total_investments"]
    }

    # 3. EMERGENCY FUND (Universal Logic)
    essential_expenses = state["user_profile"]["expenses"]["monthly_total"] - state["user_profile"]["expenses"]["components"]["investment_sips"]
    target_emergency_fund = essential_expenses * 3 
    emergency_fund_sip = 0
    months_needed = 0
    
    if state["user_profile"]["assets"]["emergency_fund"] < target_emergency_fund:
        shortfall = target_emergency_fund - state["user_profile"]["assets"]["emergency_fund"]
        
        # Max allocatable is 60% of surplus.
        max_allocatable = max(100, monthly_surplus * 0.60)
        
        months_needed = shortfall / max_allocatable
        if months_needed < 1: months_needed = 1

        emergency_fund_sip = shortfall / months_needed
        
        state["goals"].append({
            "name": "Build Emergency Fund",
            "target_amount": shortfall,
            "term": "short_term",
            "type": "Savings",
            "required_monthly_investment": emergency_fund_sip,
            "time_horizon_years": months_needed / 12,
            "achieved_by_year": int(datetime.now().year + (months_needed / 12) if (months_needed/12) > 1 else datetime.now().year)
        })

    # 4. SURPLUS & SOLVENCY CHECK (Critical Safety Layer)
    print("\n--- Processing Solvency ---")
    
    total_needs_cost = abs(required_retirement_sip) + emergency_fund_sip
    
    if total_needs_cost > monthly_surplus:
        state["solvency_status"] = "INSOLVENT"
        state["solvency_gap"] = total_needs_cost - monthly_surplus
        permanent_surplus_for_sips = 0
        cash_this_month = 0
    else:
        state["solvency_status"] = "SOLVENT"
        state["solvency_gap"] = 0
        cash_this_month = monthly_surplus - abs(required_retirement_sip)
        permanent_surplus_for_sips = cash_this_month - emergency_fund_sip

    state["user_profile"]["remaining_surplus"] = permanent_surplus_for_sips

    # 5. GOAL PROCESSING
    LOAN_INTEREST_RATE = 0.09 
    current_year = datetime.now().year
    
    total_long_term_allocated_sips = 0 
    short_term_freed_cash = 0

    for goal in state["goals"]:
        if "Build Emergency Fund" in goal["name"]: continue
            
        if "time_horizon_years" not in goal:
            if goal["term"] == "short_term": goal["time_horizon_years"] = 2
            elif goal["term"] == "medium_term": goal["time_horizon_years"] = 5
            else: goal["time_horizon_years"] = 10
        
        goal["achieved_by_year"] = int(current_year + goal["time_horizon_years"])

        inflation_adj_future_cost = npf.fv(
            rate=INFLATION_RATE,
            nper=goal["time_horizon_years"],
            pmt=0,
            pv=-goal["target_amount"]
        )
        goal["inflation_adjusted_cost"] = inflation_adj_future_cost

        # IMMEDIATE BUY CHECK
        if state["solvency_status"] == "SOLVENT" and cash_this_month > 0 and inflation_adj_future_cost < (cash_this_month * 0.80):
            goal["status"] = "IMMEDIATE_BUY"
            goal["required_monthly_investment"] = 0
            goal["message"] = "Achievable immediately!"
            goal["achieved_by_year"] = current_year
            cash_this_month -= inflation_adj_future_cost 
            continue 

        # LOAN STRATEGY CHECK
        if goal["type"] == "Loan-Assisted" or "house" in goal["name"].lower():
            goal["type"] = "Loan-Assisted" 
            down_payment_needed = inflation_adj_future_cost * 0.20
            loan_principal_amount = inflation_adj_future_cost * 0.80
            
            goal["down_payment_needed"] = down_payment_needed
            goal["loan_amount"] = loan_principal_amount
            
            loan_tenure_years = 20
            loan_end_year = goal["achieved_by_year"] + loan_tenure_years
            goal["loan_end_year"] = loan_end_year
            
            if loan_end_year > state["retirement_plan"]["retirement_year"]:
                goal["loan_warning"] = f"Warning: Loan ends in {loan_end_year}, which is after your retirement ({state['retirement_plan']['retirement_year']})."
            else:
                goal["loan_warning"] = "Safe"

            required_sip_dp = npf.pmt(
                rate=INVESTMENT_RETURN_RATE / 12,
                nper=goal["time_horizon_years"] * 12,
                pv=0,
                fv=-down_payment_needed
            )
            goal["required_monthly_investment"] = abs(required_sip_dp)

            estimated_future_emi = npf.pmt(
                rate=LOAN_INTEREST_RATE / 12,
                nper=loan_tenure_years * 12, 
                pv=-loan_principal_amount
            )
            goal["estimated_emi"] = abs(estimated_future_emi)

        # STANDARD SIP CHECK
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
        
        total_long_term_allocated_sips += goal.get("required_monthly_investment", 0)

    # 6. WEALTH ACCELERATION
    if state["solvency_status"] == "SOLVENT":
        long_term_wealth_capacity = max(0, monthly_surplus - abs(required_retirement_sip) - total_long_term_allocated_sips)
        
        if long_term_wealth_capacity > 2000:
             state["goals"].append({
                "name": "Wealth Acceleration (Post-Emergency)",
                "type": "Investment",
                "term": "ongoing",
                "time_horizon_years": 0,
                "required_monthly_investment": long_term_wealth_capacity,
                "message": "Invest surplus for long-term wealth."
             })

    # ============================================================
    # --- DETERMINISTIC ASSET ALLOCATION & DTI LOGIC ---
    # ============================================================
    
    # 1. Asset Allocation Recommendation
    risk_level = state.get("risk_appetite", "Medium")
    if risk_level == "High":
        allocation_str = "80% Equity (Index Funds/Mid-Cap) / 20% Debt"
    elif risk_level == "Low":
        allocation_str = "30% Equity (Large Cap) / 70% Debt (Bonds/FDs)"
    else: # Medium
        allocation_str = "60% Equity (Flexi-Cap) / 40% Debt"
    
    state["user_profile"]["asset_allocation_recommendation"] = allocation_str

    # 2. DTI Calculation
    m_income = state["user_profile"]["income"]["monthly_income"]
    m_emis = state["user_profile"]["expenses"]["components"]["loan_emis"]
    if m_income > 0:
        dti_value = (m_emis / m_income) * 100
    else:
        dti_value = 0
    state["user_profile"]["dti_ratio"] = dti_value
    print(f"DEBUG: Total Needs: {total_needs_cost}")
    print(f"DEBUG: Monthly Surplus: {monthly_surplus}")
    print(f"DEBUG: Solvency Status: {state['solvency_status']}")

    print(state)

    return state


def feasibility_checker(state:AgentState) ->AgentState :
    print(" ")
    print("==========================Inside Feasibility checker==========================")
    feasibility_report = warnings_generator(state)
    state['feasibility'] = feasibility_report
    return state

def plan_generator(state:AgentState) ->AgentState :


    print(" ")
    print("==========================Inside Plan generator==========================")

    final_prompt= create_master_prompt(state)
    response_text = ""


    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")


    client = Groq(api_key=api_key)

    # Send request and stream response
    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are FinCoach, a professional financial advisor in India."},
            *state.get("messages", []),
            {"role": "user", "content": final_prompt}
        ],
        stream=True  # Enable streaming
    )


    print("\nResponse:\n")
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            response_text += delta  # collect it

    print("\n\n--- End of Response ---")

    # store in state
    state["plan"] = response_text.strip()
    state["formatted_output"] = response_text.strip()
    return state

def output(state:AgentState)-> AgentState:
    print(" ")
    print("==========================Inside Output==========================")
    
    return state

def goal_parser(state:AgentState)->AgentState:
    print(" ")
    print("==========================Inside goal parser==========================")
    # Safety
    if not state.get("messages"):
        state["pending_update"] = None
        return state

    user_msg = state["messages"][-1]["content"]

    # Format goals for LLM grounding
    goals_str = ", ".join(
        f"{g['name']} ({g['target_amount']})" for g in state.get("goals", [])
    )

    system_prompt = f"""
You are an intent parser for a financial planning system.

Current goals:
{goals_str}

User wants to MODIFY something in their financial profile.

Return ONLY valid JSON in one of these formats.

GOAL UPDATE:
{{
  "action": "update",
  "entity": "goal",
  "identifier": "<exact goal name from list>",
  "field": "target_amount",
  "value": <number>
}}

RETIREMENT UPDATE:
{{
  "action": "update",
  "entity": "retirement",
  "field": "desired_retirement_age",
  "value": <number>
}}

If request is unclear or unsupported:
{{ "action": "none" }}
"""

    try:
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            response_format={"type": "json_object"}
        )

        parsed = json.loads(response.choices[0].message.content)
        print("Parsed state update:", parsed)
        state["pending_update"] = parsed

    except Exception as e:
        print("State update parsing failed:", e)
        state["pending_update"] = None

    return state
def update_state(state:AgentState)->AgentState:
    print(" ")
    print("==========================Inside update state==========================")
    update = state.get("pending_update")

    if not update or update.get("action") != "update":
        print("No valid update to apply.")
        return state

    # --- GOAL UPDATE ---
    if update["entity"] == "goal":
        for goal in state.get("goals", []):
            if goal["name"] == update["identifier"]:
                old_val = goal.get(update["field"])
                goal[update["field"]] = update["value"]
                print(
                    f"Updated goal '{goal['name']}': "
                    f"{old_val} → {update['value']}"
                )
                break

    # --- RETIREMENT UPDATE ---
    elif update["entity"] == "retirement":
        retirement_info = state["user_profile"]["retirement_info"]

        old_val = retirement_info.get(update["field"])
        retirement_info[update["field"]] = update["value"]

        print(
            f"Updated retirement field '{update['field']}': "
            f"{old_val} → {update['value']}"
        )

    # Cleanup
    state["pending_update"] = None
    return state


def general_chat(state: AgentState) -> AgentState:
    print("==========================Inside General Chat==========================")

    messages = state.get("messages")
    if not messages:
        raise RuntimeError("general_chat called with empty or missing messages")

    if messages[-1]["role"] != "user":
        raise RuntimeError("ChatView must append user message before invoking graph")

    system_prompt = get_general_chat_prompt(
        state.get("user_profile", {}).get("name", "User"),
        state.get("feasibility", {})
    )

    messages_for_llm = [
        {"role": "system", "content": system_prompt},
        *messages
    ]

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    stream = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages_for_llm,
        temperature=0.7,
        stream=True
    )

    response_text = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            response_text += delta

    state["formatted_output"] = response_text.strip()
    return state

def decider(state) -> Literal["new_user", "modify", "chat"]:
    print("==========================Inside DECIDER ==========================")
    messages = state.get("messages", [])

    if not messages:
        return "new_user"

    msg = messages[-1]["content"].lower()
    modify_keywords = ["change", "update", "modify", "what if", "increase", "decrease"]

    if any(k in msg for k in modify_keywords) and state.get("goals"):
        return "modify"

    return "chat"


graph = StateGraph(AgentState)

# Nodes
#graph.add_node("decider", decider)
graph.add_node("input_collector", input_collector)
graph.add_node("goal_classifier", goal_classifier)
graph.add_node("session_updater", session_updater)
graph.add_node("risk_predictor", risk_predictor)
graph.add_node("financial_calc", finantial_calc)
graph.add_node("feasibility_checker", feasibility_checker)
graph.add_node("plan_generator", plan_generator)
graph.add_node("goal_parser", goal_parser)
graph.add_node("update_state", update_state)
graph.add_node("general_chat", general_chat)
graph.add_node("output", output)

graph.set_conditional_entry_point(
    decider,  # The routing function
    {
        # The map of string -> node
        "new_user": "input_collector",
        "modify": "goal_parser",
        "chat": "general_chat"
    }
)

# NEW USER FLOW
graph.add_edge("input_collector", "goal_classifier")
graph.add_edge("goal_classifier", "risk_predictor")
graph.add_edge("risk_predictor", "session_updater")
graph.add_edge("session_updater", "financial_calc")
graph.add_edge("financial_calc", "feasibility_checker")
graph.add_edge("feasibility_checker", "plan_generator")
graph.add_edge("plan_generator", "output")

# MODIFY USER FLOW
graph.add_edge("goal_parser", "update_state")
graph.add_edge("update_state", "financial_calc")
graph.add_edge("financial_calc", "feasibility_checker")
graph.add_edge("feasibility_checker", "plan_generator")
graph.add_edge("plan_generator", "output")

# GENERAL CHAT FLOW
graph.add_edge("general_chat", "output")

# LOOP BACK
graph.add_edge("output", END)


# Build graph
built_graph = graph.compile()
