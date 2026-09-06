import mysql.connector
from decimal import Decimal
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '@mysql',
    'database': 'sessioninformation'
}

# -----------------------------------------------
## Data Preparation (Helper Function)
# -----------------------------------------------
def _prepare_full_data_for_db(state):
    """
    Extracts and maps ALL financial data from the complex input dictionary (state)
    to the flat structures required by ALL six MySQL tables.
    """
    input_data = state['input_data']
    financial = input_data['financial_info']
    
    # 1. user_profile Data
    personal = input_data['personal_info']
    profile_data = {
        'name': personal.get('name'),
        'age': personal.get('current_age'),
        'gender': personal.get('gender'),
        'number_of_children': personal.get('number_of_children'),
        'risk_appetite': state.get('risk_appetite', 'unknown') 
    }

    # 2. income Data
    income_data = {
        'annual_income': Decimal(financial['income'].get('annual', 0))
    }

    # 3. liabilities Data
    liabilities_source = financial['liabilities']
    liabilities_data = {
        'total_debt': Decimal(liabilities_source.get('total_debt', 0)),
    }

    # 4. assets Data
    assets_source = financial['assets']
    savings = assets_source['savings']
    portfolio = assets_source['portfolio_breakdown_percent']
    
    assets_data = {
        'epf': Decimal(savings.get('epf', 0)),
        'ppf': Decimal(savings.get('ppf', 0)),
        'nps': Decimal(savings.get('nps', 0)),
        'bank_savings': Decimal(savings.get('bank_savings', 0)),
        'total_investments': Decimal(assets_source.get('total_investments', 0)),
        'equity_percent': Decimal(portfolio.get('equity', 0)),
        'mutual_funds_percent': Decimal(portfolio.get('mutual_funds', 0)),
        'gold_percent': Decimal(portfolio.get('gold', 0)),
        'crypto_percent': Decimal(portfolio.get('crypto', 0)),
        'other_percent': Decimal(portfolio.get('other', 0)),
        'emergency_fund': Decimal(assets_source.get('emergency_fund', 0))
    }

    # 5. expenses Data
    expenses_source = financial['expenses']
    components = expenses_source['components']
    
    expenses_data = {
        'monthly_total': Decimal(expenses_source.get('monthly_total', 0)),
        'loan_emis': Decimal(components.get('loan_emis', 0)),
        'investment_sips': Decimal(components.get('investment_sips', 0)),
        'misc': Decimal(components.get('misc', 0))
    }

    # 6. goals Data
    goals_list_db = []
    for goal in state.get('goals', []):
        goals_list_db.append({
            'name': goal.get('name'),
            'term': goal.get('term'),
            'target_amount': Decimal(goal.get('target_amount', 0)),
            'type': goal.get('type')
        })
    
    return profile_data, income_data, liabilities_data, assets_data, expenses_data, goals_list_db


# -----------------------------------------------
## Main Insertion Function (Updated to insert ALL tables)
# -----------------------------------------------
def insert(state):
    """
    Parses the state dictionary and inserts data into ALL six tables.
    """
    profile_data, income_data, liabilities_data, assets_data, expenses_data, goals_list = _prepare_full_data_for_db(state)
    
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**DB_CONFIG)
        cursor = db_connection.cursor()
        print("Database connection established.")

        # --- A. Insert user_profile ---
        print("1. Inserting user profile...")
        profile_sql = "INSERT INTO user_profile (name, age, gender, number_of_children, risk_appetite) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(profile_sql, tuple(profile_data.values()))
        user_id = cursor.lastrowid
        print(f"   User profile inserted. New user_id: {user_id}")

        # --- B. Insert income ---
        print("2. Inserting income data...")
        income_sql = "INSERT INTO income (user_id, annual_income) VALUES (%s, %s)"
        cursor.execute(income_sql, (user_id, income_data['annual_income']))

        # --- C. Insert liabilities ---
        print("3. Inserting liabilities data...")
        liab_sql = "INSERT INTO liabilities (user_id, total_debt) VALUES (%s, %s)"
        cursor.execute(liab_sql, (user_id, liabilities_data['total_debt']))

        # --- D. Insert assets ---
        print("4. Inserting assets data...")
        asset_fields = ', '.join(assets_data.keys())
        asset_placeholders = ', '.join(['%s'] * len(assets_data))
        asset_sql = f"INSERT INTO assets (user_id, {asset_fields}) VALUES (%s, {asset_placeholders})"
        asset_values = (user_id,) + tuple(assets_data.values())
        cursor.execute(asset_sql, asset_values)
        
        # --- E. Insert expenses ---
        print("5. Inserting expenses data...")
        expense_sql = "INSERT INTO expenses (user_id, monthly_total, loan_emis, investment_sips, misc) VALUES (%s, %s, %s, %s, %s)"
        expense_values = (user_id, expenses_data['monthly_total'], expenses_data['loan_emis'], expenses_data['investment_sips'], expenses_data['misc'])
        cursor.execute(expense_sql, expense_values)

        # --- F. Insert goals ---
        print(f"6. Inserting {len(goals_list)} goals...")
        goal_sql = "INSERT INTO goals (user_id, name, term, target_amount, type) VALUES (%s, %s, %s, %s, %s)"
        for goal in goals_list:
            goal_values = (user_id, goal['name'], goal['term'], goal['target_amount'], goal['type'])
            cursor.execute(goal_sql, goal_values)

        db_connection.commit()
        print("\nAll SIX tables successfully populated and committed. ✅")

    except mysql.connector.Error as err:
        print(f"\nError inserting data: {err}")
        if db_connection:
            db_connection.rollback()
            print("Transaction rolled back. ❌")
    
    finally:
        if db_connection and db_connection.is_connected():
            cursor.close()
            db_connection.close()
            print("MySQL connection closed.")
