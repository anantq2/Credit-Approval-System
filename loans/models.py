from django.db import models
from customers.models import Customer
from django.utils import timezone
import uuid

def generate_loan_id():
    return f'L{timezone.now().strftime("%Y%m%d")}{str(uuid.uuid4().hex)[:8].upper()}'

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_id = models.CharField(max_length=20, unique=True, default=generate_loan_id)
    loan_amount = models.FloatField()
    tenure = models.IntegerField(help_text="in months")
    interest_rate = models.FloatField()
    monthly_repayment = models.FloatField(default=0.0)  # EMI, default added
    emis_paid_on_time = models.IntegerField(default=0)  # Default to 0
    start_date = models.DateField(default=timezone.now)  # Default to now
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # New: For easy active loan checks
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.loan_id

    # New method for repayments_left 
    @property
    def repayments_left(self):
        return self.tenure - self.emis_paid_on_time if self.tenure > self.emis_paid_on_time else 0

    #  Auto-set is_active on save
    def save(self, *args, **kwargs):
        if self.end_date and self.end_date < timezone.now().date():
            self.is_active = False
        super().save(*args, **kwargs)
