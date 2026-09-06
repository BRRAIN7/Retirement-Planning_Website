from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="marital_status",
        ),
        migrations.RemoveField(
            model_name="liabilities",
            name="monthly_debt_contribution",
        ),
        migrations.RemoveField(
            model_name="retirementinfo",
            name="retirement_lifestyle_description",
        ),
        migrations.RemoveField(
            model_name="retirementinfo",
            name="risk_tolerance_score",
        ),
        migrations.RemoveField(
            model_name="retirementinfo",
            name="investment_preferences",
        ),
        migrations.RemoveField(
            model_name="retirementinfo",
            name="annual_savings_rate_percent",
        ),
    ]
