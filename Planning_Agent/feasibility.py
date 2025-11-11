# from typing import TYPE_CHECKING
# import json

# # Import AgentState only for type hints (no runtime import)
# if TYPE_CHECKING:
#     from main import AgentState

# def warnings_generator(state: "AgentState") -> dict:
#     print("Generates various warning on checking feasibility of the entered goals")
#     feasibility_report = {
#         "foundational_solvency": {},
#         "retirement_reality_check": {},
#         "goal_details": {}
#     }

#     # --- 1. Extract All Necessary Data ---
#     try:
#         profile = state["user_profile"]
#         goals = state["goals"]
#         retirement_plan = state["retirement_plan"]

#         total_monthly_surplus = profile.get("monthly_surplus", 0)
#         remaining_surplus = profile.get("remaining_surplus", 0)
#         monthly_income = profile.get("income", {}).get("monthly_income", 0)

#         req_retirement_sip = retirement_plan.get("required_sip", 0)
#         existing_emis = profile.get("expenses", {}).get("components", {}).get("loan_emis", 0)

#         emergency_fund_sip = 0
#         for goal in goals:
#             if "Build Emergency Fund" in goal.get("name", ""):
#                 emergency_fund_sip = goal.get("required_monthly_investment", 0)
#                 break

#         total_foundation_cost = req_retirement_sip + emergency_fund_sip

#         print(f"--- Running Feasibility Checks ---")
#         print(f"Total Monthly Surplus: ₹{total_monthly_surplus:,.2f}")
#         print(f"Total Foundation (Needs) Cost: ₹{total_foundation_cost:,.2f}")
#         print(f"Remaining Surplus (for Wants): ₹{remaining_surplus:,.2f}")

#     except KeyError as e:
#         print(f"CRITICAL ERROR: Missing key {e} in state. Cannot run feasibility check.")
#         feasibility_report["foundational_solvency"] = {
#             "status": "Error",
#             "message": f"Critical data missing: {e}. Cannot perform checks."
#         }
#         state["feasibility"] = feasibility_report
#         return state

#     # --- 2. Implement the Rules ---

#     # == RULE 1: Foundational Solvency Check ==
#     if total_foundation_cost > total_monthly_surplus:
#         feasibility_report["foundational_solvency"] = {
#             "status": "Fundamentally Unaffordable",
#             "message": (
#                 f"Your essential financial foundation (Retirement: ₹{req_retirement_sip:,.2f} + "
#                 f"Emergency Fund: ₹{emergency_fund_sip:,.2f}) costs ₹{total_foundation_cost:,.2f}/month, "
#                 f"but your total monthly surplus is only ₹{total_monthly_surplus:,.2f}."
#             )
#         }
#         print(f"CRITICAL: {feasibility_report['foundational_solvency']['message']}")
#         state["feasibility"] = feasibility_report
#         return state
#     else:
#         feasibility_report["foundational_solvency"] = {
#             "status": "Foundation Secure",
#             "message": f"Your foundational needs (₹{total_foundation_cost:,.2f}) are covered by your monthly surplus."
#         }
#         print("INFO: Foundational Solvency Check: PASSED")

#     # == RULE 4: Retirement Reality Check ==
#     desired_retirement_spending = profile.get("retirement_info", {}).get("desired_retirement_expenses_inr", 0)
#     investment_sips = profile.get("expenses", {}).get("components", {}).get("investment_sips", 0)
#     current_essential_expenses = profile.get("expenses", {}).get("monthly_total", 0) - investment_sips

#     lower_bound = current_essential_expenses * 0.70
#     upper_bound = current_essential_expenses * 1.50

#     if desired_retirement_spending < lower_bound:
#         feasibility_report["retirement_reality_check"] = {
#             "status": "Review Recommended (Under-Estimate)",
#             "message": f"Your desired retirement spending (₹{desired_retirement_spending:,.0f}) is < 70% of your current essential spending (₹{current_essential_expenses:,.0f})."
#         }
#     elif desired_retirement_spending > upper_bound:
#         feasibility_report["retirement_reality_check"] = {
#             "status": "Aggressive Goal (Over-Estimate)",
#             "message": f"Your desired retirement spending (₹{desired_retirement_spending:,.0f}) is > 150% of your current spending (₹{current_essential_expenses:,.0f})."
#         }
#     else:
#         feasibility_report["retirement_reality_check"] = {
#             "status": "Seems Realistic",
#             "message": "Your desired retirement spending is in a realistic range compared to your current lifestyle."
#         }

#     print(f"INFO: Retirement Reality Check: {feasibility_report['retirement_reality_check']['status']}")

#     # == RULES 2 & 3: Individual Goal Feasibility + Affordability Ratio ==
#     print("--- Checking Individual Goals ---")

#     for goal in goals:
#         goal_name = goal.get("name", "Unknown Goal")
#         goal_details = {}

#         if "Build Emergency Fund" in goal_name:
#             goal_details = {
#                 "status": "Foundation Goal",
#                 "message": "This is a foundational need and is correctly prioritized."
#             }
#             feasibility_report["goal_details"][goal_name] = goal_details
#             continue

#         # Identify cost type
#         goal_monthly_cost = goal.get("required_monthly_investment", goal.get("estimated_emi", 0))

#         # == RULE 2: Basic Feasibility ==
#         if goal_monthly_cost > remaining_surplus:
#             goal_details["status"] = "Unrealistic"
#             goal_details["message"] = (
#                 f"This goal's monthly cost (₹{goal_monthly_cost:,.2f}) is greater than your remaining surplus (₹{remaining_surplus:,.2f})."
#             )
#             print(f"GOAL CHECK: '{goal_name}' -> Unrealistic")
#         else:
#             goal_details["status"] = " Feasible"
#             goal_details["message"] = (
#                 f"This goal's monthly cost (₹{goal_monthly_cost:,.2f}) fits within your remaining surplus."
#             )
#             print(f"GOAL CHECK: '{goal_name}' ->  Feasible")

#         # == RULE 3: Affordability Ratio ==
#         if remaining_surplus > 0:
#             affordability_ratio = goal_monthly_cost / remaining_surplus

#             if affordability_ratio > 1.0:
#                 aff_status = "Unrealistic"
#             elif affordability_ratio > 0.8:
#                 aff_status = "Very Risky"
#             elif affordability_ratio > 0.6:
#                 aff_status = "Tight Fit"
#             elif affordability_ratio > 0.3:
#                 aff_status = "Comfortable"
#             else:
#                 aff_status = "Safe"

#             goal_details["affordability_check"] = {
#                 "status": aff_status,
#                 "ratio": round(affordability_ratio, 2),
#                 "message": f"This goal consumes {affordability_ratio*100:.1f}% of your remaining surplus."
#             }

#         else:
#             goal_details["affordability_check"] = {
#                 "status": "Unrealistic",
#                 "message": "No remaining surplus available for this goal."
#             }

#         feasibility_report["goal_details"][goal_name] = goal_details

#     # --- 3. Finalize ---
#     print("\nFeasibility Check Complete. Final report:")
#     print(json.dumps(feasibility_report, indent=2))
    
#     return feasibility_report
from typing import TYPE_CHECKING
import json

# Import AgentState only for type hints (no runtime import)
if TYPE_CHECKING:
    from main import AgentState

def warnings_generator(state: "AgentState") -> dict:
    """
    Generates a comprehensive feasibility report by checking all
    foundational, goal-specific, and health-related rules.
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
        remaining_surplus = profile.get("remaining_surplus", 0)
        monthly_income = profile.get("income", {}).get("monthly_income", 1) # Use 1 to avoid ZeroDivisionError

        req_retirement_sip = retirement_plan.get("required_sip", 0)
        existing_emis = profile.get("expenses", {}).get("components", {}).get("loan_emis", 0)

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
        print(f"Existing EMIs: ₹{existing_emis:,.2f}")
        print(f"Monthly Income: ₹{monthly_income:,.2f}")

    except KeyError as e:
        print(f"CRITICAL ERROR: Missing key {e} in state. Cannot run feasibility check.")
        feasibility_report["foundational_solvency"] = {
            "status": "Error",
            "message": f"Critical data missing: {e}. Cannot perform checks."
        }
        # We don't return state here, just the report
        return feasibility_report

    # --- 2. Implement the Rules ---

    # == RULE 1: Foundational Solvency Check (Your Code) ==
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
        # This is a show-stopper. We can return the report early.
        return feasibility_report
    else:
        feasibility_report["foundational_solvency"] = {
            "status": "Foundation Secure",
            "message": f"Your foundational needs (₹{total_foundation_cost:,.2f}) are covered by your monthly surplus."
        }
        print("INFO: Foundational Solvency Check: PASSED")

    # == RULE 4: Retirement Reality Check (Your Code) ==
    desired_retirement_spending = profile.get("retirement_info", {}).get("desired_retirement_expenses_inr", 0)
    investment_sips = profile.get("expenses", {}).get("components", {}).get("investment_sips", 0)
    current_essential_expenses = profile.get("expenses", {}).get("monthly_total", 0) - investment_sips

    lower_bound = current_essential_expenses * 0.70
    upper_bound = current_essential_expenses * 1.50

    if desired_retirement_spending < lower_bound:
        feasibility_report["retirement_reality_check"] = {
            "status": "Review Recommended (Under-Estimate)",
            "message": f"Your desired retirement spending (₹{desired_retirement_spending:,.0f}) is < 70% of your current essential spending (₹{current_essential_expenses:,.0f})."
        }
    elif desired_retirement_spending > upper_bound:
        feasibility_report["retirement_reality_check"] = {
            "status": "Aggressive Goal (Over-Estimate)",
            "message": f"Your desired retirement spending (₹{desired_retirement_spending:,.0f}) is > 150% of your current spending (₹{current_essential_expenses:,.0f})."
        }
    else:
        feasibility_report["retirement_reality_check"] = {
            "status": "Seems Realistic",
            "message": "Your desired retirement spending is in a realistic range compared to your current lifestyle."
        }
    print(f"INFO: Retirement Reality Check: {feasibility_report['retirement_reality_check']['status']}")

    # == RULES 2 & 3: Individual Goal Feasibility + DTI Check (Your Code + Added Logic) ==
    print("--- Checking Individual Goals ---")

    for goal in goals:
        goal_name = goal.get("name", "Unknown Goal")
        goal_details = {}

        if "Build Emergency Fund" in goal_name:
            goal_details = {
                "status": "Foundation Goal",
                "message": "This is a foundational need and is correctly prioritized."
            }
            feasibility_report["goal_details"][goal_name] = goal_details
            continue

        goal_monthly_cost = goal.get("required_monthly_investment", goal.get("estimated_emi", 0))

        # == RULE 2: Basic Feasibility (Affordability) (Your Code) ==
        if goal_monthly_cost > remaining_surplus:
            goal_details["status"] = "Unrealistic"
            goal_details["message"] = (
                f"This goal's monthly cost (₹{goal_monthly_cost:,.2f}) is greater than your remaining surplus (₹{remaining_surplus:,.2f})."
            )
            print(f"GOAL CHECK: '{goal_name}' -> Unrealistic")
        else:
            goal_details["status"] = "Feasible"
            goal_details["message"] = (
                f"This goal's monthly cost (₹{goal_monthly_cost:,.2f}) fits within your remaining surplus."
            )
            print(f"GOAL CHECK: '{goal_name}' -> Feasible")

        # == AFFORDABILITY RATIO (Your Code) ==
        if remaining_surplus > 0:
            affordability_ratio = goal_monthly_cost / remaining_surplus
            if affordability_ratio > 1.0: aff_status = "Unrealistic"
            elif affordability_ratio > 0.8: aff_status = "Very Risky"
            elif affordability_ratio > 0.6: aff_status = "Tight Fit"
            elif affordability_ratio > 0.3: aff_status = "Comfortable"
            else: aff_status = "Safe"
            
            goal_details["affordability_check"] = {
                "status": aff_status,
                "message": f"This goal consumes {affordability_ratio*100:.1f}% of your remaining surplus."
            }
        else:
            goal_details["affordability_check"] = { "status": "Unrealistic", "message": "No remaining surplus." }
            
        
        # ==================== NEW LOGIC ADDED HERE ====================
        
        # == RULE 3: New Debt Health Check (DTI) ==
        if goal.get("type") == "Loan-Assisted" and monthly_income > 0:
            
            new_estimated_emi = goal.get("estimated_emi", 0)
            new_total_debt_load = existing_emis + new_estimated_emi
            new_dti_ratio = new_total_debt_load / monthly_income

            # Apply tiered triggers
            if new_dti_ratio > 0.50:
                dti_status = "Unmanageable"
                dti_message = f"This new loan would push your total debt to {new_dti_ratio*100:.0f}% of your income, which is dangerously high."
            elif new_dti_ratio > 0.43:
                dti_status = "High Risk"
                dti_message = f"This new loan would push your total debt to {new_dti_ratio*100:.0f}% of your income, which is a high-risk level."
            elif new_dti_ratio > 0.37:
                dti_status = "Manageable, but Tight"
                dti_message = f"Your total debt would be {new_dti_ratio*100:.0f}% of your income. This is acceptable, but your budget will be tight."
            else:
                dti_status = "Safe"
                dti_message = f"Your total debt level of {new_dti_ratio*100:.0f}% is healthy."

            # Add this check to the goal's details
            goal_details["dti_check"] = {
                "status": dti_status,
                "new_dti_ratio": round(new_dti_ratio, 2),
                "message": dti_message
            }
            print(f"GOAL CHECK: '{goal_name}' -> DTI Status: {dti_status}")
        
        # ===================== NEW LOGIC ENDS HERE =====================

        feasibility_report["goal_details"][goal_name] = goal_details

    # --- 3. Finalize ---
    print("\nFeasibility Check Complete. Final report:")
    print(json.dumps(feasibility_report, indent=2))
    
    return feasibility_report