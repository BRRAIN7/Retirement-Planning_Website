# prompts.py
def get_general_chat_prompt(user_name, feasibility_context):
    """
    Generates the system prompt for the General Chat node.
    """
    return f"""
    You are 'FinCoach', a friendly and professional financial advisor.
    You are speaking to {user_name}.

    **USER'S CURRENT FINANCIAL CONTEXT:**
    {feasibility_context}

    **YOUR INSTRUCTIONS:**
    1. **Answer Questions:** Explain financial concepts (SIP, Inflation, Debt) simply if asked.
    2. **Use Context:** If the user asks about *their* situation (e.g., "Is my plan safe?"), refer to the Context provided above.
    3. **No Math:** DO NOT try to recalculate numbers. If the user wants to change a goal (e.g., "Change car to 10L"), politely ask them to say "Update my car goal".
    4. **Tone:** Be encouraging, concise, and empathetic.
    """

def create_master_prompt(state: dict) -> str:
    """
    Takes the final AgentState and builds the complete, formatted
    prompt for the LLM.
    """
    
    # --- 1. Get all the data from the state ---
    user_profile = state.get("user_profile", {})
    risk_appetite = state.get("risk_appetite", "Medium")
    retirement_plan = state.get("retirement_plan", {})
    goals = state.get("goals", [])
    feasibility_results = state.get("feasibility", {}) # Assuming this is populated
    
    # --- 2. Calculate data needed for the prompt ---
    user_name = user_profile.get('name', 'User')

    # Debt-to-Income (DTI) and Debt Payoff calculations
    monthly_income = user_profile.get("income", {}).get("monthly_income", 1)
    existing_emis = user_profile.get("expenses", {}).get("components", {}).get("loan_emis", 0)
    dti_ratio = (existing_emis / monthly_income) * 100 if monthly_income > 0 else 0
    total_debt = user_profile.get("liabilities", {}).get("total_debt", 0)
    monthly_debt_payment = user_profile.get("liabilities", {}).get("monthly_debt_contribution", 1)
    years_to_debt_free = (total_debt / monthly_debt_payment) / 12 if monthly_debt_payment > 0 else 0

    # Find the Emergency Fund goal to get its SIP
    emergency_fund_sip = 0
    for g in goals:
        if "Build Emergency Fund" in g["name"]:
            emergency_fund_sip = g.get('required_monthly_investment', 0)
            break

    # --- 3. Build the Data Summary String ---
    data_summary = f"""

        --- USER DATA ---
        Name: {user_name}
        Age: {user_profile.get('age')}
        Risk Appetite: {risk_appetite}

        --- FINANCIAL SNAPSHOT ---
        Total Monthly Surplus: ₹{user_profile.get('monthly_surplus', 0):,.0f}
        Existing Debt-to-Income (DTI) Ratio: {dti_ratio:.0f}%
        Existing Loan EMIs: ₹{existing_emis:,.0f}
        Time to be Debt-Free (Existing Debts): {years_to_debt_free:.1f} years

        --- PRIORITY PLAN: NEEDS ---
        1. Emergency Fund:
        - Required SIP: ₹{emergency_fund_sip:,.0f}
        - Timeframe: 18 months
        - Feasibility: Healthy

        2. Retirement:
        - Corpus Target (Net): ₹{retirement_plan.get('net_corpus_to_build', 0):,.0f}
        - Required SIP: ₹{retirement_plan.get('required_sip', 0):,.0f}/month
        - Feasibility: Healthy

        --- LIFESTYLE GOALS: WANTS ---
        """

    # Loop through all OTHER goals and add them to the summary
    for goal in goals:
        if "Build Emergency Fund" in goal["name"] or "debt" in goal["name"].lower():
            continue
        
        goal_name = goal.get('name')
        feasibility = feasibility_results.get(goal_name, {}).get('status', 'Healthy')
        
        goal_details = f"Goal: {goal_name} (Term: {goal.get('term')})\n"
        goal_details += f"   - Feasibility: {feasibility}\n"
        
        if goal.get('type') == 'Loan-Assisted':
            goal_details += f"   - Down Payment Needed: ₹{goal.get('down_payment_needed', 0):,.0f}\n"
            goal_details += f"   - Estimated EMI: ₹{goal.get('estimated_emi', 0):,.0f}/month\n"
        else:
            goal_details += f"   - Required SIP: ₹{goal.get('required_monthly_investment', 0):,.0f}/month\n"
            
        data_summary += goal_details

    # --- 4. Build the Master Prompt Template ---
    master_prompt = f"""
        You are "FinCoach," a professional, encouraging, and expert financial advisor in India.
        Your task is to write a comprehensive, personalized financial plan for the user based ONLY on the data summary provided.
        Address the user by their name. Your tone must be simple, positive, and clear. Do not use complex jargon.
        You MUST ignore any user-entered goals related to "paying off debt," as you will provide a dedicated plan for this.

        --- YOUR PLAN STRUCTURE (MUST FOLLOW) ---

        1.  **"Hello, {user_name}!"**: Start with a warm, brief introduction.

        2.  **"Your Financial Snapshot"**: Give a quick overview of their situation. Mention their **Total Monthly Surplus** and their existing **DTI ratio**.

        3.  **"Your Financial Waterfall: A Step-by-Step Plan"**: This is the most important section. You must explain how their money will be allocated in phases.

            * **Phase 1: Your Foundation (Today)**
                * Explain their "Needs First" plan. Detail their top-priority SIPs:
                    * **Emergency Fund:** (State the monthly SIP of ₹{emergency_fund_sip:,.0f} and the 18-month timeframe).
                    * **Retirement:** (State the required monthly SIP of ₹{retirement_plan.get('required_sip', 0):,.0f}).
                * Explain that their "Remaining Surplus" will be used for their other goals.

            * **Phase 2: The Goal Accelerator (After 18 Months)**
                * Congratulate them on completing their Emergency Fund.
                * Explain that their **₹{emergency_fund_sip:,.0f}/month** SIP is now "freed up."
                * Instruct them to "waterfall" this new cash onto their next highest-priority lifestyle goal (e.g., the car down payment or vacation).

            * **Phase 3: The Debt-Free Milestone (After {years_to_debt_free:.1f} years)**
                * Congratulate them on paying off their existing debts.
                * State that their old "Existing Loan EMI" of **₹{existing_emis:,.0f}/month** is now "freed up."
                * **Strongly advise** them to "waterfall" this large new cash flow toward their most important long-term goals.

        4.  **"Your Lifestyle Goals (Wants)"**:
            * Go through each lifestyle goal from the data summary (except debt goals).
            * **For 'Loan-Assisted' Goals:** You MUST explain the two-part plan: 1) A short-term savings plan for the `down_payment_needed` and 2) The long-term commitment of the `estimated_emi`.
            * **For 'Feasibility: Healthy'**: Confirm the plan is good.
            * **For 'Feasibility: Unrealistic'**: Gently explain it's not affordable *right now*.
            * **For 'Feasibility: Unhealthy'**: Explain *why* (e.g., "The new EMI would push your DTI over the safe 40% limit...").

        5.  **"Your Retirement Strategy"**:
            * Based on their `{risk_appetite}` risk profile, recommend a simple, diversified portfolio for their retirement SIP.

        6.  **"Final Thoughts"**: End with a short, encouraging summary.

        --- DATA SUMMARY ---
        {data_summary}
        --- END OF DATA ---

        Now, write the complete, personalized financial plan for {user_name}.
        """
    
    # --- 5. Return the final prompt ---
    return master_prompt



# import json

# def create_master_prompt(state: dict) -> str:
#     """
#     Takes the final AgentState (with the new feasibility format) and 
#     builds the complete, formatted prompt for the LLM.
#     """
    
#     # --- 1. Get all the data from the state ---
#     user_profile = state.get("user_profile", {})
#     risk_appetite = state.get("risk_appetite", "Medium")
#     retirement_plan = state.get("retirement_plan", {})
#     goals = state.get("goals", [])
#     feasibility_report = state.get("feasibility", {}) # Get the full report

#     # --- 2. Calculate data needed for the prompt ---
#     user_name = user_profile.get('name', 'User')

#     # Financial & Debt calculations
#     monthly_income = user_profile.get("income", {}).get("monthly_income", 1)
#     existing_emis = user_profile.get("expenses", {}).get("components", {}).get("loan_emis", 0)
#     dti_ratio = (existing_emis / monthly_income) * 100 if monthly_income > 0 else 0
#     total_debt = user_profile.get("liabilities", {}).get("total_debt", 0)
#     monthly_debt_payment = user_profile.get("liabilities", {}).get("monthly_debt_contribution", 1)
#     years_to_debt_free = (total_debt / monthly_debt_payment) / 12 if monthly_debt_payment > 0 else 0

#     # Find the Emergency Fund goal to get its SIP
#     emergency_fund_sip = 0
#     for g in goals:
#         if "Build Emergency Fund" in g["name"]:
#             emergency_fund_sip = g.get('required_monthly_investment', 0)
#             break

#     # Get overall plan status
#     plan_status = feasibility_report.get("foundational_solvency", {}).get("status", "Error")

#     # --- 3. Build the Data Summary String ---
#     data_summary = f"""
# --- USER DATA ---
# Name: {user_name}
# Age: {user_profile.get('age')}
# Risk Appetite: {risk_appetite}

# --- FINANCIAL SNAPSHOT ---
# Overall Plan Status: {plan_status}
# Total Monthly Surplus: ₹{user_profile.get('monthly_surplus', 0):,.0f}
# Existing Debt-to-Income (DTI) Ratio: {dti_ratio:.0f}%
# Existing Loan EMIs: ₹{existing_emis:,.0f}
# Time to be Debt-Free (Existing Debts): {years_to_debt_free:.1f} years

# --- PRIORITY PLAN: NEEDS ---
# 1. Emergency Fund:
#    - Required SIP: ₹{emergency_fund_sip:,.0f}
#    - Timeframe: 18 months

# 2. Retirement:
#    - Corpus Target (Net): ₹{retirement_plan.get('net_corpus_to_build', 0):,.0f}
#    - Required SIP: ₹{retirement_plan.get('required_sip', 0):,.0f}/month

# --- LIFESTYLE GOALS: WANTS (with Feasibility) ---
# """

#     # Loop through all OTHER goals and add them to the summary
#     goal_details_report = feasibility_report.get("goal_details", {})
    
#     for goal in goals:
#         goal_name = goal.get("name")
#         # Skip priority goals AND any user-entered debt goals
#         if "Build Emergency Fund" in goal_name or "debt" in goal_name.lower():
#             continue
        
#         # Get the specific feasibility checks for this goal
#         goal_feasibility = goal_details_report.get(goal_name, {})
        
#         goal_details = f"Goal: {goal_name} (Term: {goal.get('term')})\n"
        
#         # Extract the key feasibility statuses
#         overall_status = goal_feasibility.get('status', 'Feasible')
#         affordability_status = goal_feasibility.get('affordability_check', {}).get('status', 'Safe')
#         dti_status = goal_feasibility.get('dti_check', {}).get('status', 'Safe')

#         goal_details += f"   - Feasibility: {overall_status}\n"
#         goal_details += f"   - Affordability: {affordability_status}\n"
#         goal_details += f"   - Debt Health: {dti_status}\n"

#         if goal.get('type') == "Loan-Assisted":
#             goal_details += f"   - Down Payment Needed: ₹{goal.get('down_payment_needed', 0):,.0f}\n"
#             goal_details += f"   - Estimated EMI: ₹{goal.get('estimated_emi', 0):,.0f}/month\n"
#         else:
#             goal_details += f"   - Required SIP: ₹{goal.get('required_monthly_investment', 0):,.0f}/month\n"
            
#         data_summary += goal_details

#     # Add the Retirement Reality Check
#     retirement_check = feasibility_report.get("retirement_reality_check", {})
#     if retirement_check.get("status") != "Seems Realistic":
#         data_summary += f"\n--- ADVISOR NOTE: RETIREMENT ---
# - Status: {retirement_check.get('status')}
# - Message: {retirement_check.get('message')}
# "

#     # --- 4. Build the Master Prompt Template ---
#     master_prompt = f"""
# You are "FinCoach," a professional, encouraging, and expert financial advisor in India.
# Your task is to write a comprehensive, personalized financial plan for the user based ONLY on the data summary provided.
# Address the user by their name. Your tone must be simple, positive, and clear. Do not use complex jargon.
# You MUST ignore any user-entered goals related to "paying off debt," as you will provide a dedicated plan for this.

# --- YOUR PLAN STRUCTURE (MUST FOLLOW) ---

# 1.  **"Hello, {user_name}!"**: Start with a warm, brief introduction.

# 2.  **"Your Financial Snapshot"**: Give a quick overview of their situation. Mention their **Total Monthly Surplus** and their **Overall Plan Status** (e.g., "Foundation Secure").

# 3.  **"Your Financial Waterfall: A Step-by-Step Plan"**: This is the most important section. You must explain how their money will be allocated in phases.

#     * **Phase 1: Your Foundation (Today)**
#         * Explain their "Needs First" plan. Detail their top-priority SIPs:
#             * **Emergency Fund:** (State the monthly SIP of ₹{emergency_fund_sip:,.0f} and the 18-month timeframe).
#             * **Retirement:** (State the required monthly SIP of ₹{retirement_plan.get('required_sip', 0):,.0f}).
#         * Explain that their "Remaining Surplus" will be used for their other goals.

#     * **Phase 2: The Goal Accelerator (After 18 Months)**
#         * Congratulate them on completing their Emergency Fund.
#         * Explain that their **₹{emergency_fund_sip:,.0f}/month** SIP is now "freed up."
#         * Instruct them to "waterfall" this new cash onto their next highest-priority lifestyle goal.

#     * **Phase 3: The Debt-Free Milestone (After {years_to_debt_free:.1f} years)**
#         * Congratulate them on paying off their existing debts.
#         * State that their old "Existing Loan EMI" of **₹{existing_emis:,.0f}/month** is now "freed up."
#         * **Strongly advise** them to "waterfall" this large new cash flow toward their most important long-term goals.

# 4.  **"Your Lifestyle Goals (Wants)"**:
#     * Go through each lifestyle goal from the data summary.
#     * **For 'Loan-Assisted' Goals:** You MUST explain the two-part plan: 1) A short-term savings plan for the `down_payment_needed` and 2) The long-term commitment of the `estimated_emi`.
    
#     * **(YOUR NEW COMPROMISE LOGIC HERE)**
#     * **If a goal's Feasibility is 'Unrealistic' or Affordability is 'Very Risky'**:
#         * You MUST explain that this goal is not affordable right now with their current surplus.
#         * **Then, you MUST proactively suggest a compromise.** For example: "This goal isn't feasible right now, but you could achieve it by..." (e.g., "focusing on increasing your income," or "waiting until after your debt is paid off").
    
#     * **If a goal's Debt Health is 'High Risk' or 'Unmanageable'**:
#         * You MUST explain why this is dangerous (e.g., "This new loan would push your total debt to a high-risk 45% of your income.").
#         * **Then, you MUST proactively suggest a compromise.** For example: "**To keep your plan safe, I strongly recommend compromising on this goal** by looking for a smaller car or saving for a larger down payment."

# 5.  **"Your Retirement Strategy"**:
#     * Based on their `{risk_appetite}` risk profile, recommend a simple, diversified portfolio for their retirement SIP.

# 6.  **"Advisor's Notes"**:
#     * **If there is an 'ADVISOR NOTE: RETIREMENT' in the data summary**, you must politely mention it. (e.g., "A quick note on your retirement budget: you've set it much lower than your current spending. I recommend reviewing this number...").

# 7.  **"Final Thoughts"**: End with a short, encouraging summary.

# --- DATA SUMMARY ---
# {data_summary}
# --- END OF DATA ---

# Now, write the complete, personalized financial plan for {user_name}.
# """
    
#     # --- 5. Return the final prompt ---
#     return master_prompt