import os
import pickle
import joblib
import pandas as pd
import random
from sklearn.preprocessing import LabelEncoder

# --- 1. DEFINE CONSTANTS ---

# Get the directory of the current script (ML_models.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Risk Model Constants ---
RISK_MODEL_FILE = os.path.join(BASE_DIR, 'risk_appetite_model.pkl')
MODEL_FEATURES = [
    'current_age', 'number_of_children', 'desired_retirement_age',
    'annual_income', 'total_debt', 'emergency_fund',
    'portfolio_percent_equity', 'portfolio_percent_crypto', 
    'portfolio_percent_gold', 'short_term_goal_amount'
]

# --- Goal Model Constants (NEW) ---
GOAL_MODEL_FILE = os.path.join(BASE_DIR, 'goal_classifier_model.joblib')
# Features from your image
GOAL_MODEL_FEATURES = ['goal_text', 'target_amount', 'goal_term'] 


# --- 2. LOAD MODEL ASSETS (ONCE) ---

# --- Risk Model ---
def _load_risk_model_assets():
    """Private function to load risk model assets from disk."""
    try:
        with open(RISK_MODEL_FILE, 'rb') as file:
            pipeline = pickle.load(file)
        
        encoder = LabelEncoder()
        encoder.fit(['High', 'Low', 'Medium']) 
        
        print(f"Risk model '{RISK_MODEL_FILE}' loaded successfully.")
        return pipeline, encoder
        
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Model file '{RISK_MODEL_FILE}' not found.")
        return None, None
    except Exception as e:
        print(f"CRITICAL ERROR loading risk model: {e}")
        return None, None

# --- Goal Model (SIMPLIFIED) ---
def _load_goal_model_assets():
    """Private function to load the goal classifier model."""
    try:
        with open(GOAL_MODEL_FILE, 'rb') as f:
            pipeline = joblib.load(f)
        
        # --- NO LABEL ENCODER NEEDED HERE ---
        # The pipeline itself seems to be outputting the string.

        print(f"Goal model '{GOAL_MODEL_FILE}' loaded successfully.")
        return pipeline  # <-- Only return the pipeline
        
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Model file '{GOAL_MODEL_FILE}' not found.")
        return None
    except Exception as e:
        print(f"CRITICAL ERROR loading goal model: {e}")
        return None

# Load all models into global variables
RISK_MODEL_PIPELINE, RISK_LABEL_ENCODER = _load_risk_model_assets()
GOAL_MODEL_PIPELINE = _load_goal_model_assets() # <-- Updated


# --- 3. PREDICTION FUNCTIONS ---

def risk_appetite_pred(user_data: dict) -> str:
    # ... (This function is correct, no changes needed) ...
    pass

# --- 4. YOUR GOAL CLASSIFICATION FUNCTION (FIXED) ---

def get_goal_classification(goal_text: str, target_amount: float, goal_term: str) -> str:
    """
    Predicts the classification ("Savings", "Investment", "Loan-Assisted")
    for a single financial goal using the trained model.
    """
    print(f"Classifying goal: {goal_text}")

    # Check if the model failed to load
    if not GOAL_MODEL_PIPELINE:
        print("Goal model not loaded. Defaulting to 'Investment'.")
        return "Investment"

    try:
        # 1. Format data for the model based on your image
        model_input = {
            "goal_text": [goal_text],
            "target_amount": [target_amount],
            "goal_term": [goal_term]
        }
        input_df = pd.DataFrame(model_input)
        input_df_features = input_df[GOAL_MODEL_FEATURES] 

        # 2. Get prediction (this is already a string, e.g., ['Savings'])
        prediction_label = GOAL_MODEL_PIPELINE.predict(input_df_features)
        
        # 3. Just return the string prediction
        return prediction_label[0]

    except Exception as e:
        print(f"Error during goal prediction: {e}. Defaulting to 'Investment'.")
        return "Investment"