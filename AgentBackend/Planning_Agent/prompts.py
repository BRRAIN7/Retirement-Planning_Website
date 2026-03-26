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
    Final optimized prompt generator.
    - Forces deterministic math (DTI, Asset Allocation).
    - Uses Data Masking for Insolvent users to prevent harmful encouragement.
    - Implements Silent Skipping for empty sections.
    """
    
    # --- 1. DATA EXTRACTION ---
    profile = state.get("user_profile", {})
    retirement_plan = state.get("retirement_plan", {})
    goals = state.get("goals", [])
    user_name = profile.get('name', 'User')
    
    # Pre-formatted Financial Values
    surplus_val = profile.get('monthly_surplus', 0)
    surplus_str = f"₹{surplus_val:,.0f}"
    dti_str = f"{profile.get('dti_ratio', 0):.1f}%"
    allocation_rec = profile.get("asset_allocation_recommendation", "60% Equity / 40% Debt")

    # Solvency Logic
    solvency_status = state.get("solvency_status")
    print(f"DEBUG: Solvency Status: {solvency_status}")
    solvency_gap = state.get("solvency_gap", 0)

    # --- 2. EMERGENCY FUND ACTION STRING ---
    emergency_fund_sip = 0
    emergency_fund_target = 0
    emergency_fund_months = 0
    for g in goals:
        if "Build Emergency Fund" in g["name"]:
            emergency_fund_sip = g.get('required_monthly_investment', 0)
            emergency_fund_target = g.get('target_amount', 0)
            emergency_fund_months = g.get('time_horizon_years', 0) * 12 
            break
            
    if emergency_fund_months <= 0:
         ef_action_str = "Status: **Secure**. You have sufficient emergency savings."
    elif emergency_fund_months < 1.5:
        ef_action_str = f"Target: ₹{emergency_fund_target:,.0f}. Action: Allocate ₹{emergency_fund_sip:,.0f} **this month** and finish it next month."
    else:
        ef_action_str = f"Target: ₹{emergency_fund_target:,.0f}. Action: Save ₹{emergency_fund_sip:,.0f}/month for {emergency_fund_months:.1f} months."

    # --- 3. GOAL BUCKETING (DATA MASKING APPLIED) ---
    immediate_str = ""
    short_term_str = ""
    long_term_str = ""
    wealth_str = ""

    # Only process lifestyle goals if the user is SOLVENT. 
    # This prevents the LLM from seeing/praising goals in a deficit.
    if solvency_status == "SOLVENT":
        for goal in goals:
            if "Build Emergency Fund" in goal["name"]: continue
            
            goal_name = goal.get('name')
            status = goal.get('status', 'PENDING')
            achieved_year = goal.get('achieved_by_year', 'N/A')
            
            details = f"Goal: {goal_name}\n"
            
            if status == "IMMEDIATE_BUY":
                details += f"   - Action: BUY NOW using this month's cash.\n"
                immediate_str += details + "\n"
            elif "Wealth Acceleration" in goal_name:
                details += f"   - Strategy: Invest Remaining Surplus\n"
                details += f"   - Monthly SIP: ₹{goal.get('required_monthly_investment', 0):,.0f}\n"
                wealth_str += details + "\n"
            else:
                if goal.get('type') == 'Loan-Assisted':
                    details += f"   - Strategy: Save Down Payment now, Take Loan in {achieved_year}.\n"
                    details += f"   - Step 1 (Save Now): Monthly SIP of ₹{goal.get('required_monthly_investment', 0):,.0f}\n"
                    details += f"   - Step 2 (Future Loan): Loan Amount ₹{goal.get('loan_amount', 0):,.0f}\n"
                    details += f"   - Future EMI Estimate: ~₹{goal.get('estimated_emi', 0):,.0f}\n"
                    if "Warning" in goal.get('loan_warning', ''):
                        details += f"   - NOTE: {goal.get('loan_warning')}\n"
                else:
                    details += f"   - Monthly SIP: ₹{goal.get('required_monthly_investment', 0):,.0f}\n"
                    details += f"   - Target Year: {achieved_year}\n"
                
                if goal.get('term') == 'short_term':
                    short_term_str += details + "\n"
                else:
                    long_term_str += details + "\n"

    # --- 4. CONDITIONAL PROMPT GENERATION ---

    if solvency_status == "INSOLVENT":
        # RESCUE MODE: Strict instructions to sound the alarm
        return f"""
        You are "FinCoach." The user {user_name} is in a CRITICAL FINANCIAL DEFICIT. 
        Your task is to sound the alarm and prioritize survival.
        
        **CRITICAL DATA:**
        * Monthly Surplus: {surplus_str}
        * Total Required for Foundation (Retirement + EF): ₹{abs(retirement_plan.get('required_sip', 0)) + emergency_fund_sip:,.0f}/month
        * Monthly Shortfall: -₹{solvency_gap:,.0f}

        **STRICT INSTRUCTIONS:**
        1. Start with "Hello {user_name}."
        2. Header: "### URGENT: FINANCIAL REALITY CHECK".
        3. Explicitly state: "Your current goals require ₹{abs(retirement_plan.get('required_sip', 0)) + emergency_fund_sip:,.0f} per month, but you only have {surplus_str}."
        4. COMMAND: Tell them they MUST pause discretionary goals (like Gaming Consoles or Trips) immediately.
        5. Priority 1: Save the entire {surplus_str} into the Emergency Fund.
        6. Priority 2: Focus on increasing income or drastically cutting expenses.
        7. Tone: Serious, Direct, and Action-Oriented. Do NOT use words like "Great start," "Commend," or "Pleased to present."
        """

    # GROWTH MODE: Standard professional presentation
    # Section headers only appear if there is data
    section_immediate = f"\n**IMMEDIATE ACTIONS**\n{immediate_str}" if immediate_str else ""
    section_short = f"\n**SHORT TERM GOALS**\n{short_term_str}" if short_term_str else ""
    section_long = f"\n**LONG TERM GOALS**\n{long_term_str}" if long_term_str else ""
    section_wealth = f"\n**WEALTH BUILDING**\n{wealth_str}" if wealth_str else ""

    return f"""
    You are "FinCoach." Present the following financial plan to {user_name}.
    
    **RULES:**
    1. USE THE NUMBERS PROVIDED. Do not recalculate or invent goals.
    2. SILENT SKIPPING: Do not mention sections (Immediate, Short Term, etc.) that are missing from the Data.
    3. Tone: Professional, Concise, and Encouraging.

    --- 1. SNAPSHOT ---
    * Monthly Surplus: {surplus_str}
    * Debt Health (DTI): {dti_str}

    --- 2. FOUNDATION ---
    * Emergency Fund: {ef_action_str}
    * Retirement: SIP ₹{retirement_plan.get('required_sip', 0):,.0f}/month. (Target: ₹{retirement_plan.get('gross_corpus', 0):,.0f})

    --- 3. GOAL STRATEGY ---
    {section_immediate}{section_short}{section_long}{section_wealth}

    --- 4. INVESTMENT STRATEGY ---
    * Recommended Allocation: {allocation_rec}

    Write the response now.
    """