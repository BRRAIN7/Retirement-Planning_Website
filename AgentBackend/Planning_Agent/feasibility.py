from typing import TYPE_CHECKING
import json

# Import AgentState only for type hints (no runtime import)
if TYPE_CHECKING:
    from main import AgentState

def warnings_generator(state: "AgentState") -> dict:
    """
    Generates a comprehensive feasibility report by checking all
    foundational, goal-specific, and health-related rules.
    Includes Cumulative Budgeting to prevent double-counting surplus.
    """
    print("Generates various warning on checking feasibility of the entered goals")
    feasibility_report = {
        "foundational_solvency": {},
        "retirement_reality_check": {},
        "goal_details": {}
    }

    # --- 1. Extract All Necessary Data ---
    try:
        profile = state["user_profile"]
        goals = state["goals"]
        retirement_plan = state["retirement_plan"]

        total_monthly_surplus = profile.get("monthly_surplus", 0)
        
        # This is the Master Surplus we start with for Lifestyle goals
        # (Surplus - Retirement SIP - Emergency Fund SIP)
        # We grab this from the profile where the calculator calculated it.
        remaining_surplus = profile.get("remaining_surplus", 0) 
        
        monthly_income = profile.get("income", {}).get("monthly_income", 1) 

        req_retirement_sip = retirement_plan.get("required_sip", 0)
        existing_emis = profile.get("expenses", {}).get("components", {}).get("loan_emis", 0)

        # Get Emergency Fund SIP specifically for Foundation Check
        emergency_fund_sip = 0
        for goal in goals:
            if "Build Emergency Fund" in goal.get("name", ""):
                emergency_fund_sip = goal.get("required_monthly_investment", 0)
                break

        total_foundation_cost = req_retirement_sip + emergency_fund_sip

        print(f"--- Running Feasibility Checks ---")
        print(f"Total Monthly Surplus: ₹{total_monthly_surplus:,.2f}")
        print(f"Total Foundation (Needs) Cost: ₹{total_foundation_cost:,.2f}")
        print(f"Remaining Surplus (for Wants): ₹{remaining_surplus:,.2f}")

    except KeyError as e:
        print(f"CRITICAL ERROR: Missing key {e} in state. Cannot run feasibility check.")
        feasibility_report["foundational_solvency"] = {
            "status": "Error",
            "message": f"Critical data missing: {e}. Cannot perform checks."
        }
        return feasibility_report

    # --- 2. Implement the Rules ---

    # == RULE 1: Foundational Solvency Check ==
    if total_foundation_cost > total_monthly_surplus:
        feasibility_report["foundational_solvency"] = {
            "status": "Fundamentally Unaffordable",
            "message": (
                f"Your essential financial foundation (Retirement: ₹{req_retirement_sip:,.2f} + "
                f"Emergency Fund: ₹{emergency_fund_sip:,.2f}) costs ₹{total_foundation_cost:,.2f}/month, "
                f"but your total monthly surplus is only ₹{total_monthly_surplus:,.2f}."
            )
        }
        print(f"CRITICAL: {feasibility_report['foundational_solvency']['message']}")
        return feasibility_report # Stop here if basics aren't met
    else:
        feasibility_report["foundational_solvency"] = {
            "status": "Foundation Secure",
            "message": f"Your foundational needs (₹{total_foundation_cost:,.2f}) are covered by your monthly surplus."
        }
        print("INFO: Foundational Solvency Check: PASSED")

    # == RULE 2: Retirement Reality Check ==
    desired_retirement_spending = profile.get("retirement_info", {}).get("desired_retirement_expenses_inr", 0)
    investment_sips = profile.get("expenses", {}).get("components", {}).get("investment_sips", 0)
    current_essential_expenses = profile.get("expenses", {}).get("monthly_total", 0) - investment_sips

    lower_bound = current_essential_expenses * 0.70
    upper_bound = current_essential_expenses * 1.50

    if desired_retirement_spending < lower_bound:
        feasibility_report["retirement_reality_check"] = {
            "status": "Review Recommended (Under-Estimate)",
            "message": f"Your desired retirement spending (₹{desired_retirement_spending:,.0f}) is < 70% of your current essential spending."
        }
    elif desired_retirement_spending > upper_bound:
        feasibility_report["retirement_reality_check"] = {
            "status": "Aggressive Goal (Over-Estimate)",
            "message": f"Your desired retirement spending (₹{desired_retirement_spending:,.0f}) is > 150% of your current spending."
        }
    else:
        feasibility_report["retirement_reality_check"] = {
            "status": "Seems Realistic",
            "message": "Your desired retirement spending is in a realistic range compared to your current lifestyle."
        }

    # == RULE 3: Individual Goal Feasibility + Cumulative Check ==
    print("--- Checking Individual Goals ---")
    
    # FIX: Initialize Running Surplus tracker
    running_surplus_tracker = remaining_surplus

    for goal in goals:
        goal_name = goal.get("name", "Unknown Goal")
        goal_details = {}

        # Skip Emergency Fund (Already handled in Foundation Check)
        if "Build Emergency Fund" in goal_name:
            goal_details = {
                "status": "Foundation Goal",
                "message": "This is a foundational need and is correctly prioritized."
            }
            feasibility_report["goal_details"][goal_name] = goal_details
            continue
            
        # Skip Wealth Acceleration (It absorbs whatever is left, doesn't need a check)
        if "Wealth Acceleration" in goal_name:
             goal_details = {
                "status": "Surplus Allocation",
                "message": "This utilizes remaining cash after all other goals."
            }
             feasibility_report["goal_details"][goal_name] = goal_details
             continue

        # Determine monthly cost (SIP or EMI)
        goal_monthly_cost = goal.get("required_monthly_investment", 0)
        
        # 3A. Absolute Check (Isolation)
        if goal_monthly_cost > remaining_surplus:
            goal_details["status"] = "Unrealistic"
            goal_details["message"] = (
                f"Cost (₹{goal_monthly_cost:,.0f}) exceeds total available surplus (₹{remaining_surplus:,.0f})."
            )
        
        # 3B. FIX: Cumulative Check (Sequence)
        elif goal_monthly_cost > running_surplus_tracker:
            goal_details["status"] = "Unrealistic (Cumulative)"
            goal_details["message"] = (
                f"Feasible alone, but unaffordable because previous goals used up the budget. "
                f"Available: ₹{running_surplus_tracker:,.0f}, Needed: ₹{goal_monthly_cost:,.0f}."
            )
        
        else:
            goal_details["status"] = "Feasible"
            goal_details["message"] = "Fits comfortably within your budget."
            # Only subtract from running tracker if it's feasible
            running_surplus_tracker -= goal_monthly_cost
            

        # 3C. Affordability Ratio (Risk Gauge)
        if remaining_surplus > 0:
            affordability_ratio = goal_monthly_cost / remaining_surplus
            if affordability_ratio > 1.0: aff_status = "Unrealistic"
            elif affordability_ratio > 0.8: aff_status = "Very Risky"
            elif affordability_ratio > 0.6: aff_status = "Tight Fit"
            elif affordability_ratio > 0.3: aff_status = "Comfortable"
            else: aff_status = "Safe"
            
            goal_details["affordability_check"] = {
                "status": aff_status,
                "ratio": f"{affordability_ratio*100:.1f}%"
            }
        else:
            goal_details["affordability_check"] = { "status": "Unrealistic", "message": "Zero Surplus" }
            
        
        # 3D. Debt-to-Income (DTI) Check for Future Loans
        if goal.get("type") == "Loan-Assisted" and monthly_income > 0:
            
            new_estimated_emi = goal.get("estimated_emi", 0)
            new_total_debt_load = existing_emis + new_estimated_emi
            new_dti_ratio = new_total_debt_load / monthly_income

            if new_dti_ratio > 0.50:
                dti_status = "Unmanageable"
                dti_msg = "Dangerously high DTI (>50%). Banks will reject this."
            elif new_dti_ratio > 0.43:
                dti_status = "High Risk"
                dti_msg = "High risk DTI (>43%)."
            elif new_dti_ratio > 0.35:
                dti_status = "Tight"
                dti_msg = "Acceptable but tight budget."
            else:
                dti_status = "Safe"
                dti_msg = "Healthy debt levels."

            goal_details["dti_check"] = {
                "status": dti_status,
                "new_dti_ratio": f"{new_dti_ratio*100:.1f}%",
                "message": dti_msg
            }
        
        # Save details
        feasibility_report["goal_details"][goal_name] = goal_details

    # --- 3. Finalize ---
    print("\nFeasibility Check Complete.")
    # print(json.dumps(feasibility_report, indent=2))
    
    return feasibility_report