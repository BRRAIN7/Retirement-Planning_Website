import mysql.connector


def insert(state) :
    print("Inserting session data into MySQL database...")

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@mysql",
            database="SessionInformation"
        )
        cursor = conn.cursor()

        # Extract data from state
        user_profile = state.get("user_profile", {})
        goals = state.get("goals", [])

        print("User profile:", user_profile)
        print("Goals:", goals)

        # Prepare user data
        user_name = user_profile.get("name", "Unknown")
        current_age = user_profile.get("age", 0)
        desired_retirement_age = user_profile.get("desired_retirement_age", 65)
        monthly_income_inr = user_profile.get("monthly_income_inr", 10000)
        annual_savings_rate_percent = user_profile.get("annual_savings_rate_percent", 0)
        marital_status = user_profile.get("marital_status", "Unknown")
        number_of_children = user_profile.get("number_of_children", 0)
        retirement_lifestyle_description = user_profile.get("retirement_lifestyle_description", "")
        investment_preferences = user_profile.get("investment_preferences", "")
        desired_retirement_expenses_inr = user_profile.get("desired_retirement_expenses_inr", 0)

        # Insert user profile into retirement_plans
        cursor.execute('''
            INSERT INTO retirement_plans (
                user_name, current_age, desired_retirement_age, monthly_income_inr,
                annual_savings_rate_percent, marital_status, number_of_children,
                retirement_lifestyle_description, investment_preferences, desired_retirement_expenses_inr
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            user_name, current_age, desired_retirement_age, monthly_income_inr,
            annual_savings_rate_percent, marital_status, number_of_children,
            retirement_lifestyle_description, investment_preferences, desired_retirement_expenses_inr
        ))
        print("Inserted user profile into retirement_plans table.")

        # Insert goals into respective tables
        cursor.execute("SELECT LAST_INSERT_ID()")
        plan_id = cursor.fetchone()[0]
        print("Inserted retirement plan with plan_id:", plan_id)

        for goal in goals:
            category = goal.get("category", "").lower()
            goal_name = goal.get("name", "")
            description = f"Target amount: {goal.get('target_amount', 0)}"

            if category == "short_term":
                cursor.execute('''
                    INSERT INTO short_term_goals (plan_id, goal_name, description)
                    VALUES (%s, %s, %s)
                ''', (plan_id, goal_name, description))
                print(f"Inserted short-term goal: {goal_name}, description: {description}")

            elif category == "medium_term":
                cursor.execute('''
                    INSERT INTO mid_term_goals (plan_id, goal_name, description)
                    VALUES (%s, %s, %s)
                ''', (plan_id, goal_name, description))
                print(f"Inserted medium-term goal: {goal_name}, description: {description}")

            elif category == "long_term":
                cursor.execute('''
                    INSERT INTO long_term_goals (plan_id, goal_name, description)
                    VALUES (%s, %s, %s)
                ''', (plan_id, goal_name, description))
                print(f"Inserted long-term goal: {goal_name}, description: {description}")


        conn.commit()
        print("All data committed successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")



