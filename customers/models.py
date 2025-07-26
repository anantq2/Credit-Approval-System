from django.db import models
from django.utils import timezone
import uuid

def generate_customer_id():
    return f'C{timezone.now().strftime("%Y%m%d")}{str(uuid.uuid4().hex)[:8].upper()}'

class Customer(models.Model):
    customer_id = models.CharField(max_length=20, unique=True, default=generate_customer_id)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_income = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)  
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"
