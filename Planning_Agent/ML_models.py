import random 
list1 =["high","medium","low"]
list2=["Savings","Loan-Assisted","Investment"] #etc


def risk_appetite_pred() -> str:
    print("Returns the risk appetire of the user")
    return random.choice(list1)

def goal_classification(state: dict) -> dict:
    print("Goals are classified here (shortterm, longterm, midterm)")

    # Assuming state contains goals
    goals = state.get("input_data", {}).get("goals", {})

    # Create a list to hold classified goals
    classified_goals = []

    # Iterate over each category and goal list
    for category, goals_list in goals.items():
        for goal in goals_list:
            # Randomly assign a goal type (e.g., "Loan-Assisted", "Investment")
            goal_type = random.choice(list2)

            # Create a new goal dictionary with term, name, target amount, and type
            classified_goal = {
                "name": goal.get("name"),
                "term": category,  # short_term, medium_term, long_term
                "target_amount": goal.get("target_amount"),
                "type": goal_type
            }

            # Add the classified goal to the list
            classified_goals.append(classified_goal)


    return classified_goals