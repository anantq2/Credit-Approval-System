# Generated by Django 5.2.4 on 2025-07-23 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_customer_approved_limit_customer_monthly_income'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='current_debt',
            field=models.IntegerField(default=0),
        ),
    ]
