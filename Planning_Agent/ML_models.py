import random 
list1 =["high","medium","low"]
list2=["Savings","Loan-Assisted","Investment"] #etc


def risk_appetite_pred() -> str:
    print("Returns the risk appetire of the user")
    return random.choice(list1)

def goal_classification():
    print("Goals are classified here (shortterm ,longterm,, midterm)")
    return random.choice(list2)