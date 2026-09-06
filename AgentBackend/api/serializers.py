from rest_framework import serializers
from .models import UserProfile, Income, Liabilities, Assets, Expenses, Goal, RetirementInfo

# ------------------------------------------------------
# HELPER SERIALIZERS (Structure matches Frontend)
# ------------------------------------------------------

class PersonalInfoSerializer(serializers.Serializer):
    name = serializers.CharField()
    current_age = serializers.IntegerField(min_value=18, max_value=100)
    gender = serializers.CharField()
    number_of_children = serializers.IntegerField(min_value=0)

class IncomeInputSerializer(serializers.Serializer):
    annual = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)

class ExpenseComponentsSerializer(serializers.Serializer):
    loan_emis = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    investment_sips = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    misc = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)

class ExpensesInputSerializer(serializers.Serializer):
    monthly_total = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    components = ExpenseComponentsSerializer()

class SavingsSerializer(serializers.Serializer):
    epf = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    ppf = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    nps = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    bank_savings = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)

class PortfolioPercentSerializer(serializers.Serializer):
    equity = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    mutual_funds = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    gold = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    crypto = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    other = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)

    # VALIDATION: Ensure percentages sum to 100
    def validate(self, data):
        total = (
            data.get('equity', 0) + 
            data.get('mutual_funds', 0) + 
            data.get('gold', 0) + 
            data.get('crypto', 0) + 
            data.get('other', 0)
        )
        # Allow 0 (if user hasn't filled it) or 100. Reject partials like 95%.
        if total != 100 and total != 0:
            raise serializers.ValidationError(f"Portfolio percentages sum to {total}%, but must equal 100%.")
        return data

class AssetsInputSerializer(serializers.Serializer):
    savings = SavingsSerializer()
    total_investments = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    portfolio_breakdown_percent = PortfolioPercentSerializer()
    emergency_fund = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)

class LiabilitiesInputSerializer(serializers.Serializer):
    total_debt = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)

class FinancialInfoSerializer(serializers.Serializer):
    income = IncomeInputSerializer()
    expenses = ExpensesInputSerializer()
    assets = AssetsInputSerializer()
    liabilities = LiabilitiesInputSerializer()

class GoalItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    target_amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)

class GoalsSerializer(serializers.Serializer):
    short_term = serializers.ListSerializer(child=GoalItemSerializer())
    medium_term = serializers.ListSerializer(child=GoalItemSerializer())
    long_term = serializers.ListSerializer(child=GoalItemSerializer())

class RetirementInfoSerializer(serializers.Serializer):
    desired_retirement_age = serializers.IntegerField(min_value=40, max_value=100)
    desired_retirement_expenses_inr = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0)

# ------------------------------------------------------
# FINAL MASTER SERIALIZER
# ------------------------------------------------------

class FinancialInputSerializer(serializers.Serializer):
    personal_info = PersonalInfoSerializer()
    financial_info = FinancialInfoSerializer()
    goals = GoalsSerializer()
    retirement_info = RetirementInfoSerializer()

    # --------------------------------------------------
    # THE DB MAPPING LOGIC
    # --------------------------------------------------
    def save_data(self, user):
        """
        Custom method to unpack the validated nested data 
        and save it to the separate Django Models.
        """
        data = self.validated_data
        
        # 1. User Profile
        p_info = data['personal_info']
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'name': p_info['name'],
                'age': p_info['current_age'],
                'gender': p_info['gender'],
                'number_of_children': p_info['number_of_children'],
            }
        )

        # 2. Income
        Income.objects.update_or_create(
            user=user,
            defaults={'annual_income': data['financial_info']['income']['annual']}
        )

        # 3. Liabilities
        liab = data['financial_info']['liabilities']
        Liabilities.objects.update_or_create(
            user=user,
            defaults={
                'total_debt': liab['total_debt'],
            }
        )

        # 4. Assets (Unpacking the nested layers)
        assets_in = data['financial_info']['assets']
        savings = assets_in['savings']
        breakdown = assets_in['portfolio_breakdown_percent']
        
        Assets.objects.update_or_create(
            user=user,
            defaults={
                'epf': savings['epf'],
                'ppf': savings['ppf'],
                'nps': savings['nps'],
                'bank_savings': savings['bank_savings'],
                'total_investments': assets_in['total_investments'],
                'equity_percent': breakdown['equity'],
                'mutual_funds_percent': breakdown['mutual_funds'],
                'gold_percent': breakdown['gold'],
                'crypto_percent': breakdown['crypto'],
                'other_percent': breakdown['other'],
                'emergency_fund': assets_in['emergency_fund']
            }
        )

        # 5. Expenses
        exp = data['financial_info']['expenses']
        comps = exp['components']
        Expenses.objects.update_or_create(
            user=user,
            defaults={
                'monthly_total': exp['monthly_total'],
                'loan_emis': comps['loan_emis'],
                'investment_sips': comps['investment_sips'],
                'misc': comps['misc']
            }
        )

        # 6. Goals (Delete old ones, insert new ones)
        Goal.objects.filter(user=user).delete()
        
        # Helper to create goals
        def create_goals(goal_list, term_type):
            for g in goal_list:
                Goal.objects.create(
                    user=user,
                    name=g['name'],
                    term=term_type,
                    target_amount=g['target_amount']
                )

        goals_data = data['goals']
        create_goals(goals_data['short_term'], 'short_term')
        create_goals(goals_data['medium_term'], 'medium_term')
        create_goals(goals_data['long_term'], 'long_term')

        # 7. Retirement Info
        ret = data['retirement_info']
        RetirementInfo.objects.update_or_create(
            user=user,
            defaults={
                'desired_retirement_age': ret['desired_retirement_age'],
                'desired_retirement_expenses_inr': ret['desired_retirement_expenses_inr'],
            }
        )