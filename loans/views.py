from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Loan
from .serializers import LoanSerializer, LoanCreateSerializer, CheckEligibilitySerializer
from customers.models import Customer
import math
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)  # For logging errors

#  loan_list view (added logging for POST errors)
@api_view(['GET', 'POST'])
def loan_list(request):
    if request.method == 'GET':
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LoanCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            loan_serializer = LoanSerializer(serializer.instance)
            return Response(loan_serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Loan creation error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#  loan_detail view (added logging for PUT errors)
@api_view(['GET', 'PUT', 'DELETE'])
def loan_detail(request, pk):
    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LoanSerializer(loan)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LoanCreateSerializer(loan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            loan_serializer = LoanSerializer(serializer.instance)
            return Response(loan_serializer.data)
        logger.error(f"Loan update error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        loan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CheckEligibilityView 

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Eligibility validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)

        credit_score = self.calculate_credit_score(customer, loans)

        approval = False
        corrected_rate = data['interest_rate']
        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50 and data['interest_rate'] > 12:
            approval = True
            corrected_rate = max(corrected_rate, 12)
        elif 10 < credit_score <= 30 and data['interest_rate'] > 16:
            approval = True
            corrected_rate = max(corrected_rate, 16)

        monthly_installment = self.calculate_emi(data['loan_amount'], corrected_rate, data['tenure'])

        current_emis = sum(loan.monthly_repayment for loan in loans if loan.is_active)
        if approval and (current_emis + monthly_installment) > 0.5 * customer.monthly_income:
            approval = False

        response = {
            "customer_id": data['customer_id'],
            "approval": approval,
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": corrected_rate,
            "tenure": data['tenure'],
            "monthly_installment": monthly_installment
        }
        return Response(response, status=status.HTTP_200_OK)

    def calculate_credit_score(self, customer, loans):
        if not loans:
            return 100

        paid_on_time = sum(1 for loan in loans if loan.emis_paid_on_time >= loan.tenure)
        total_loans = len(loans)
        current_year = timezone.now().year
        loans_this_year = sum(1 for loan in loans if loan.start_date.year == current_year)
        loan_volume = sum(loan.loan_amount for loan in loans)
        current_loans_sum = sum(loan.loan_amount for loan in loans if loan.is_active)
        if current_loans_sum > customer.approved_limit:
            return 0

        score = (paid_on_time / max(total_loans, 1) * 40) + (loans_this_year * 20) + (loan_volume / 10000 * 10)
        return min(100, int(score))

    def calculate_emi(self, principal, rate, tenure):
        monthly_rate = rate / 12 / 100
        if monthly_rate == 0:
            return principal / tenure
        return principal * monthly_rate * math.pow(1 + monthly_rate, tenure) / (math.pow(1 + monthly_rate, tenure) - 1)

# CreateLoanView (kept as is)
class CreateLoanView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Loan creation validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)

        credit_score = self.calculate_credit_score(customer, loans)

        approval = False
        corrected_rate = data['interest_rate']
        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50 and data['interest_rate'] > 12:
            approval = True
            corrected_rate = max(corrected_rate, 12)
        elif 10 < credit_score <= 30 and data['interest_rate'] > 16:
            approval = True
            corrected_rate = max(corrected_rate, 16)

        monthly_installment = self.calculate_emi(data['loan_amount'], corrected_rate, data['tenure'])

        current_emis = sum(loan.monthly_repayment for loan in loans if loan.is_active)
        if approval and (current_emis + monthly_installment) > 0.5 * customer.monthly_income:
            approval = False

        if not approval:
            return Response({
                "loan_id": None,
                "customer_id": data['customer_id'],
                "loan_approved": False,
                "message": "Loan not approved based on eligibility",
                "monthly_installment": 0
            }, status=status.HTTP_400_BAD_REQUEST)

        start_date = timezone.now().date()
        end_date = start_date + relativedelta(months=data['tenure'])
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=data['loan_amount'],
            tenure=data['tenure'],
            interest_rate=corrected_rate,
            monthly_repayment=monthly_installment,
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date
        )

        customer.current_debt += data['loan_amount']
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": data['customer_id'],
            "loan_approved": True,
            "message": "Loan approved and created",
            "monthly_installment": monthly_installment
        }, status=status.HTTP_201_CREATED)

    def calculate_credit_score(self, customer, loans):
        if not loans:
            return 100

        paid_on_time = sum(1 for loan in loans if loan.emis_paid_on_time >= loan.tenure)
        total_loans = len(loans)
        current_year = timezone.now().year
        loans_this_year = sum(1 for loan in loans if loan.start_date.year == current_year)
        loan_volume = sum(loan.loan_amount for loan in loans)
        current_loans_sum = sum(loan.loan_amount for loan in loans if loan.is_active)
        if current_loans_sum > customer.approved_limit:
            return 0

        score = (paid_on_time / max(total_loans, 1) * 40) + (loans_this_year * 20) + (loan_volume / 10000 * 10)
        return min(100, int(score))

    def calculate_emi(self, principal, rate, tenure):
        monthly_rate = rate / 12 / 100
        if monthly_rate == 0:
            return principal / tenure
        return principal * monthly_rate * math.pow(1 + monthly_rate, tenure) / (math.pow(1 + monthly_rate, tenure) - 1)

# ViewLoanView 
class ViewLoanView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)  
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoanSerializer(loan)
        response = serializer.data
        
        response['customer'] = {
            "customer_id": loan.customer.customer_id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age
        }
        return Response(response, status=status.HTTP_200_OK)

# ViewLoansView 
class ViewLoansView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)
        if not loans:
            return Response({"message": "No loans found for this customer"}, status=status.HTTP_200_OK)

        response = []
        for loan in loans:
            response.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "repayments_left": loan.tenure - loan.emis_paid_on_time
            })
        return Response(response, status=status.HTTP_200_OK)
