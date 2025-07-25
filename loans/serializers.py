from rest_framework import serializers
from .models import Loan
from customers.serializers import CustomerSerializer
from customers.models import Customer  # Imported for validation in CheckEligibilitySerializer
import math  # Imported for EMI calculation 

class LoanSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = ('loan_id', 'created_at')

class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment',
                 'emis_paid_on_time', 'start_date', 'end_date']

# CheckEligibilitySerializer for /check-eligibility endpoint 
class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.CharField(max_length=20)
    loan_amount = serializers.FloatField(min_value=0)
    interest_rate = serializers.FloatField(min_value=0)
    tenure = serializers.IntegerField(min_value=1)

    def validate_customer_id(self, value):
        if not Customer.objects.filter(customer_id=value).exists():
            raise serializers.ValidationError("Customer does not exist")
        return value
