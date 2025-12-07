from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    number_of_children = models.IntegerField(null=True, blank=True)
    risk_appetite = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Income(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="income")
    annual_income = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.user.username} Income"


class Liabilities(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="liabilities")
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    monthly_debt_contribution = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.user.username} Liabilities"


class Assets(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="assets")


    epf = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    ppf = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    nps = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    bank_savings = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    total_investments = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    equity_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    mutual_funds_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    gold_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    crypto_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    other_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    emergency_fund = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.user.username} Assets"


class Expenses(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="expenses")

    monthly_total = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    loan_emis = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    investment_sips = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    misc = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.user.username} Expenses"


class Goal(models.Model):
    TERM_CHOICES = [
        ('short_term', 'Short Term'),
        ('medium_term', 'Medium Term'),
        ('long_term', 'Long Term'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, null=True)
    term = models.CharField(max_length=20, choices=TERM_CHOICES, null=True)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    type = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"{self.user.username} Goal: {self.name}"


class MessageHistory(models.Model):
    """
    Stores limited chat history per user.
    We’ll only ever use the last N messages when building AgentState.
    """
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.user.username} [{self.role}] {self.timestamp}"
class RetirementInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="retirement_info")

    desired_retirement_age = models.IntegerField(null=True, blank=True)
    retirement_lifestyle_description = models.TextField(null=True, blank=True)
    desired_retirement_expenses_inr = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    risk_tolerance_score = models.IntegerField(null=True, blank=True)
    investment_preferences = models.TextField(null=True, blank=True)
    annual_savings_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} RetirementInfo"
