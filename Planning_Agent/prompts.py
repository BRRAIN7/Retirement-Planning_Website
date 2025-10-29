# prompts.py

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