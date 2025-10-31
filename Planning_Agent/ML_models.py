import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
import random # Keep this for your goal_classification function

# --- 1. DEFINE CONSTANTS ---

# Get the directory of the current script (ML_models.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the model file (assuming it's in the same Planning_Agent folder)
MODEL_FILE = os.path.join(BASE_DIR, 'risk_appetite_model.pkl')

# The *exact* 10 features your model was trained on
MODEL_FEATURES = [
    'current_age', 'number_of_children', 'desired_retirement_age',
    'annual_income', 'total_debt', 'emergency_fund',
    'portfolio_percent_equity', 'portfolio_percent_crypto', 
    'portfolio_percent_gold', 'short_term_goal_amount'
]

# --- 2. LOAD MODEL ASSETS (ONCE) ---
# This code runs ONE TIME when the server starts.
def _load_model_assets():
    """Private function to load model assets from disk."""
    try:
        with open(MODEL_FILE, 'rb') as file:
            pipeline = pickle.load(file)
        
        encoder = LabelEncoder()
        # Fit on the exact class names from your training
        encoder.fit(['High', 'Low', 'Medium']) 
        
        print(f"Risk model '{MODEL_FILE}' loaded successfully.")
        return pipeline, encoder
        
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Model file '{MODEL_FILE}' not found.")
        return None, None
    except Exception as e:
        print(f"CRITICAL ERROR loading model: {e}")
        return None, None

# Load the model into global variables
RISK_MODEL_PIPELINE, RISK_LABEL_ENCODER = _load_model_assets()

# --- 3. YOUR PREDICTION FUNCTION (FIXED) ---

def risk_appetite_pred(user_data: dict) -> str:
    """
    Predicts the risk appetite of the user based on input data.
    This REPLACES your random.choice placeholder.
    """
    print("Running real-time risk appetite prediction...")

    # Check if the model failed to load
    if not RISK_MODEL_PIPELINE:
        print("Model is not loaded. Returning 'Medium' as default.")
        return "Medium" # Return a safe default

    try:
        # 1. Format data for the model
        input_df = pd.DataFrame([user_data])
        # Re-order columns to *exactly* match the training data
        input_df_features = input_df[MODEL_FEATURES]

        # 2. Get prediction (pipeline handles scaling)
        prediction_numeric = RISK_MODEL_PIPELINE.predict(input_df_features)
        
        # 3. Map to label
        prediction_label = RISK_LABEL_ENCODER.inverse_transform(prediction_numeric)
        
        # 4. Return the label
        return prediction_label[0]

    except KeyError as e:
        print(f"Error during prediction: Missing key {e}. Check input data.")
        return "Medium" # Return a safe default
    except Exception as e:
        print(f"Error during prediction: {e}. Returning 'Medium' as default.")
        return "Medium"

# --- 4. YOUR GOAL CLASSIFICATION FUNCTION (UNCHANGED) ---
list2=["Savings","Loan-Assisted","Investment"] #etc



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