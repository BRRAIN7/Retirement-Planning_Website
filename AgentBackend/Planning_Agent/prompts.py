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
    
    # --- 2. Calculate data needed for the prompt ---
    user_name = user_profile.get('name', 'User')

    monthly_income = user_profile.get("income", {}).get("monthly_income", 1)
    existing_emis = user_profile.get("expenses", {}).get("components", {}).get("loan_emis", 0)
    dti_ratio = (existing_emis / monthly_income) * 100 if monthly_income > 0 else 0
    
    # Find the Emergency Fund details
    emergency_fund_sip = 0
    emergency_fund_months = 0
    for g in goals:
        if "Build Emergency Fund" in g["name"]:
            emergency_fund_sip = g.get('required_monthly_investment', 0)
            emergency_fund_months = g.get('time_horizon_years', 0) * 12 
            break
            
    # Format time string nicely
    if emergency_fund_months <= 0:
         ef_time_str = "Already Complete (0 months)"
    elif emergency_fund_months < 1.0:
        ef_time_str = "less than 1 month"
    elif emergency_fund_months < 1.5:
        ef_time_str = "approx. 4-6 weeks"
    else:
        ef_time_str = f"{emergency_fund_months:.1f} months"

    # --- 3. Build the Data Summary String ---
    data_summary = f"""
        --- USER DATA ---
        Name: {user_name}
        Risk Appetite: {risk_appetite}
        Total Monthly Surplus: ₹{user_profile.get('monthly_surplus', 0):,.0f}
        Existing DTI Ratio: {dti_ratio:.0f}%
        
        --- PRIORITY PLAN: NEEDS ---
        1. Emergency Fund:
           - Required SIP: ₹{emergency_fund_sip:,.0f}
           - Timeframe: {ef_time_str}
           - Status: Crucial Foundation

        2. Retirement:
           - Required SIP: ₹{retirement_plan.get('required_sip', 0):,.0f}/month
           - Feasibility: Mandatory

        --- LIFESTYLE & WEALTH GOALS ---
        """

    for goal in goals:
        if "Build Emergency Fund" in goal["name"]: continue
        
        goal_name = goal.get('name')
        achieved_year = goal.get('achieved_by_year', 'N/A')
        status = goal.get('status', 'PENDING')
        
        goal_details = f"Goal: {goal_name}\n"
        goal_details += f"   - Term: {goal.get('term', 'Unknown')}\n"
        goal_details += f"   - Status: {status}\n"

        if status == "IMMEDIATE_BUY":
            goal_details += f"   - Action: BUY NOW using this month's cash.\n"
        
        elif goal.get('type') == 'Loan-Assisted':
            goal_details += f"   - Action: Save for Down Payment (₹{goal.get('down_payment_needed', 0):,.0f})\n"
            goal_details += f"   - Monthly SIP: ₹{goal.get('required_monthly_investment', 0):,.0f}\n"
            goal_details += f"   - Future Loan EMI (Est): ₹{goal.get('estimated_emi', 0):,.0f}\n"
            goal_details += f"   - Target Year: {achieved_year}\n"
        
        elif "Wealth Acceleration" in goal_name:
             goal_details += f"   - Action: Invest Surplus (Post-Emergency)\n"
             goal_details += f"   - Monthly SIP: ₹{goal.get('required_monthly_investment', 0):,.0f}\n"
             goal_details += f"   - Note: This is your capacity once Emergency Fund is done.\n"
        
        else:
            goal_details += f"   - Monthly SIP: ₹{goal.get('required_monthly_investment', 0):,.0f}\n"
            goal_details += f"   - Target Year: {achieved_year}\n"
            goal_details += f"   - Future Snowball Cash Available: ₹{goal.get('future_snowball_cash', 0):,.0f}\n"

        data_summary += goal_details + "\n"

    # --- 4. Build the Master Prompt Template ---
    master_prompt = f"""
        You are "FinCoach," an expert financial advisor.
        Your task is to write a personalized financial plan based ONLY on the data below.
        
        **CRITICAL INSTRUCTIONS:**
        1. **Immediate Wins:** If a goal has status "IMMEDIATE_BUY", celebrate it! Tell the user they can buy it *this month* using their cash flow. Do NOT suggest a SIP for these.
        2. **Future Loans:** For "Loan-Assisted" goals (like Houses), explain: "We are saving for the Down Payment now. You will take the loan in [Target Year]." (Read the Target Year from the goal data).
        3. **Wealth Creation:** If "Wealth Acceleration" is listed, explain: "Once your Emergency Fund is secure (Timeframe: {ef_time_str}), invest this surplus into Flexi-Cap funds."
        4. **Tone:** Professional, Encouraging, and Clear.

        --- YOUR PLAN STRUCTURE ---

        1.  **"Hello, {user_name}!"**: Brief, warm intro.

        2.  **"Your Financial Snapshot"**: Mention Total Surplus and DTI.

        3.  **"The Priority Foundation"**:
            * **Emergency Fund:** You must build this in **{ef_time_str}** by saving ₹{emergency_fund_sip:,.0f}/month.
            * **Retirement:** Commit ₹{retirement_plan.get('required_sip', 0):,.0f}/month.

        4.  **"Your Goal Strategy" (The Core Plan)**:
            * **Immediate Wins (If any):** List items they can buy TODAY.
            * **Short Term Goals:** Explain the SIPs.
            * **Long Term Goals:** Explain the "Down Payment Strategy" (Don't save the full cash, save the down payment). Mention the Target Year.
            * **Wealth Acceleration:** Advise investing the "Wealth Acceleration" amount once the Emergency Fund is complete.

        5.  **"Investment Advice"**:
            * Based on `{risk_appetite}` risk, suggest an asset allocation (Equity vs Debt).

        --- DATA SUMMARY ---
        {data_summary}
        --- END OF DATA ---

        Write the plan now.
        """
    
    return master_prompt


