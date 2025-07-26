from rest_framework import serializers
from .models import Customer  # Import the actual model from models.py

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer  # References the model from models.py
        fields = '__all__'

# New serializer for registration (fixed inheritance and imports)
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()  # For combining first and last name in response

    class Meta:
        model = Customer  # References the model from models.py
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_income', 'phone_number', 'name']  # Added 'name' if needed
        read_only_fields = ['customer_id']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
        # Calculate approved_limit: 36 * monthly_income, rounded to nearest lakh
        monthly_income = validated_data.get('monthly_income', 0)
        approved_limit = round(36 * monthly_income / 100000) * 100000
        customer = Customer.objects.create(
            approved_limit=approved_limit,
            current_debt=0,  
            **validated_data
        )
        return customer

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = self.get_name(instance)
        representation['monthly_income'] = instance.monthly_income
        representation['approved_limit'] = instance.approved_limit
        return representation
