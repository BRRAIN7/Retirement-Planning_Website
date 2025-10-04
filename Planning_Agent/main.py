from typing import TypedDict
from langgraph.graph import StateGraph,START,END
import mysql.connector


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
    print("Here the inputs will be collected which are received from the frontend")
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
    print ("Node 2")
    state["goals"]=goal_classification(state)
    
    print("Agent state after classificatino:  ",state["goals"])
    return state





def session_updater(state: AgentState) -> AgentState:
    print (" ")
    # print("Inserting session data into MySQL database...")

    # conn = None
    # cursor = None

    # try:
    #     conn = mysql.connector.connect(
    #         host="localhost",
    #         user="root",
    #         password="anvesha",
    #         database="my_database"
    #     )
    #     cursor = conn.cursor()

    #     # Extract data from state
    #     user_profile = state.get("user_profile", {})
    #     goals = state.get("goals", [])

    #     print("User profile:", user_profile)
    #     print("Goals:", goals)

    #     # Prepare user data
    #     user_name = user_profile.get("name", "Unknown")
    #     current_age = user_profile.get("age", 0)
    #     desired_retirement_age = user_profile.get("desired_retirement_age", 65)
    #     monthly_income_inr = user_profile.get("monthly_income_inr", 10000)
    #     annual_savings_rate_percent = user_profile.get("annual_savings_rate_percent", 0)
    #     marital_status = user_profile.get("marital_status", "Unknown")
    #     number_of_children = user_profile.get("number_of_children", 0)
    #     retirement_lifestyle_description = user_profile.get("retirement_lifestyle_description", "")
    #     investment_preferences = user_profile.get("investment_preferences", "")
    #     desired_retirement_expenses_inr = user_profile.get("desired_retirement_expenses_inr", 0)

    #     # Insert user profile into retirement_plans
    #     cursor.execute('''
    #         INSERT INTO retirement_plans (
    #             user_name, current_age, desired_retirement_age, monthly_income_inr,
    #             annual_savings_rate_percent, marital_status, number_of_children,
    #             retirement_lifestyle_description, investment_preferences, desired_retirement_expenses_inr
    #         )
    #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     ''', (
    #         user_name, current_age, desired_retirement_age, monthly_income_inr,
    #         annual_savings_rate_percent, marital_status, number_of_children,
    #         retirement_lifestyle_description, investment_preferences, desired_retirement_expenses_inr
    #     ))
    #     print("Inserted user profile into retirement_plans table.")

    #     # Insert goals into respective tables
    #     cursor.execute("SELECT LAST_INSERT_ID()")
    #     plan_id = cursor.fetchone()[0]
    #     print("Inserted retirement plan with plan_id:", plan_id)

    #     for goal in goals:
    #         category = goal.get("category", "").lower()
    #         goal_name = goal.get("name", "")
    #         description = f"Target amount: {goal.get('target_amount', 0)}"

    #         if category == "short_term":
    #             cursor.execute('''
    #                 INSERT INTO short_term_goals (plan_id, goal_name, description)
    #                 VALUES (%s, %s, %s)
    #             ''', (plan_id, goal_name, description))
    #             print(f"Inserted short-term goal: {goal_name}, description: {description}")

    #         elif category == "medium_term":
    #             cursor.execute('''
    #                 INSERT INTO mid_term_goals (plan_id, goal_name, description)
    #                 VALUES (%s, %s, %s)
    #             ''', (plan_id, goal_name, description))
    #             print(f"Inserted medium-term goal: {goal_name}, description: {description}")

    #         elif category == "long_term":
    #             cursor.execute('''
    #                 INSERT INTO long_term_goals (plan_id, goal_name, description)
    #                 VALUES (%s, %s, %s)
    #             ''', (plan_id, goal_name, description))
    #             print(f"Inserted long-term goal: {goal_name}, description: {description}")


    #             conn.commit()
    #             print("All data committed successfully.")

    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")

    # finally:
    #     if conn and conn.is_connected():
    #         cursor.close()
    #         conn.close()
    #         print("MySQL connection closed.")

    # return state



def risk_predictor(state:AgentState) ->AgentState :
  
    risk= risk_appetite_pred()
    state["risk_appetite"]=risk
    print(f"Risk of the user is :{risk}")
    return state

def finantial_calc(state:AgentState) -> AgentState:
    print("calculates the loans or saving or investments for goals")
    return state

def feasibility_checker(state:AgentState) ->AgentState :
    print("Receives the output of the feasibility checker")
    return state

def plan_generator(state:AgentState) ->AgentState :
    print("Generates plan")
    return state

def output(state:AgentState)-> AgentState:
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
graph.add_edge("goal_classifier","session_updater")
graph.add_edge("session_updater","risk_predictor")
graph.add_edge("risk_predictor","finantial_calc")
graph.add_edge("finantial_calc","feasibility_checker")
graph.add_edge("feasibility_checker","plan_generator")
graph.add_edge("plan_generator","output")
graph.add_edge("output",END)

built_graph= graph.compile()


# if __name__ == "__main__":
#     sample_state = {
#         "input_data": {
#             "personal_info": {
#                 "name": "Aryan Kumar",
#                 "current_age": 30,
#                 "gender": "Male",
#                 "marital_status": "Married",
#                 "number_of_children": 1
#             },
#             "goals": {
#                 "short_term": [
#                     {"name": "International Vacation", "target_amount": 300000}
#                 ],
#                 "medium_term": [
#                     {"name": "Buy a Car", "target_amount": 500000}
#                 ],
#                 "long_term": [
#                     {"name": "Child's Higher Education", "target_amount": 2500000}
#                 ]
#             }
#         }
#     }

#     updated_state = input_collector(sample_state)
#     print("Output from input_collector:\n", updated_state)

#     updated_state = goal_classification(updated_state)
#     print("Output from goal_classifier:\n", updated_state)

#     updated_state = input_collector(sample_state)
#     updated_state = goal_classifier(updated_state)
#     updated_state = session_updater(updated_state)

#     print(updated_state)



