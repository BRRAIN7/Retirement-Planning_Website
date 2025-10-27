def plan_generator(state:AgentState) ->AgentState :
    data_summary = f"""
            --- USER PROFILE ---
            Name: {state['user_profile']['name']}
            Age: {state['user_profile']['age']}
            Risk Appetite: {state['risk_appetite']}

            --- FINANCIALS ---
            Total Monthly Surplus: ₹{state['user_profile']['monthly_surplus']:,}
            Remaining Surplus (for lifestyle goals): ₹{state['user_profile']['remaining_surplus']:,}

            --- PRIORITY PLAN ---
            1. Retirement:
            - Corpus Target: ₹{state['retirement_plan']['net_corpus_to_build']:,}
            - Required SIP: ₹{state['retirement_plan']['required_sip']:,}/month
            - Feasibility: Healthy

            2. Emergency Fund:
            - Goal: Build Emergency Fund
            - Required SIP: ₹{emergency_fund_sip:,}/month for 18 months
            - Feasibility: Healthy

            --- LIFESTYLE GOALS ---
            1. Goal: {state['goals'][0]['name']}
            - Type: {state['goals'][0]['type']}
            - Cost: ₹{state['goals'][0]['required_monthly_investment']:,}/month
            - Feasibility: Healthy

            2. Goal: {state['goals'][1]['name']}
            - Type: {state['goals'][1]['type']}
            - Down Payment Needed: ₹{state['goals'][1]['down_payment_needed']:,}
            - Estimated EMI: ₹{state['goals'][1]['estimated_emi']:,}/month
            - Feasibility: Healthy
            """

    user_name = state['user_profile']['name']

    master_prompt = f"""
    You are "FinCoach," a professional, friendly, and encouraging financial advisor in India.
    Your task is to write a personalized financial plan for a user named {user_name}.
    Address them directly and use simple, clear language. Avoid jargon.

    The plan MUST be based ONLY on the data summary provided below. Do not make up any numbers.

    --- YOUR PLAN STRUCTURE ---

    1.  **"Hello, {user_name}!"**: Start with a warm, brief introduction.
    2.  **"Your Financial Snapshot"**: Give a quick, positive overview of their financial situation, mentioning their total monthly surplus.
    3.  **"Your Priority Plan (Needs First)"**:
        * This is the most important section.
        * First, explain their **Retirement Plan** (the corpus target and the required SIP).
        * Second, explain their **Emergency Fund** plan (the SIP and the 18-month timeframe).
    4.  **"Your Lifestyle Goals (Wants)"**:
        * Explain that this plan uses their "Remaining Surplus."
        * For **each goal** in the data summary, you MUST follow this logic:
        * **If Feasibility is 'Healthy_&_Achievable'**: Congratulate them and describe the plan (e.g., "For your vacation, you'll invest ₹X per month.").
        * **If Feasibility is 'Achievable_but_Unhealthy'**: Gently explain *why* it's unhealthy (e.g., "The EMI for this car is too high for your income"). Then, provide an alternative (e.g., "I recommend looking for a car with an EMI closer to ₹Y...").
        * **If Feasibility is 'Unrealistic'**: Explain that this goal is not affordable with their current surplus. Advise them to focus on their priority goals first.
        * **For 'Loan-Assisted' goals**: You MUST explain the two-part plan: 1) A short-term savings plan for the 'down_payment_needed' and 2) The long-term commitment of the 'estimated_emi'.
    5.  **"Your Portfolio Strategy"**:
        * Based on their `{state['risk_appetite']}` risk profile, recommend a simple, diversified portfolio for their retirement SIP. (e.g., for 'Medium' risk, suggest a 70/30 split between Nifty 50 Index Funds and PPF/Debt Funds).
    6.  **"Final Thoughts"**: End with a short, encouraging summary.

    --- DATA SUMMARY ---
    {data_summary}
    --- END OF DATA ---

    Now, write the complete, personalized financial plan for {user_name}.
    """
    print(" ")
    print("==========================Inside Plan generator==========================")

    result=ollama.chat(
        model="phi3:mini",
        messages=[
            
            {"role":"user","content":master_prompt},
        ],

        stream=True,
    )

    for i in result:
        print(i["message"]["content"],end="",flush=True)

    return state