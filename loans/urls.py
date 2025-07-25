from django.urls import path
from .views import loan_list, loan_detail, CheckEligibilityView, CreateLoanView, ViewLoanView, ViewLoansView  
urlpatterns = [
    # Loan list and create
    path('', loan_list, name='loan_list'),

    # Loan detail
    path('<int:pk>/', loan_detail, name='loan_detail'),

    # Check eligibility
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check_eligibility'),

    # Create loan
    path('create-loan/', CreateLoanView.as_view(), name='create_loan'),

    # View specific loan
    path('view-loan/<str:loan_id>/', ViewLoanView.as_view(), name='view_loan'),

    # View all loans for customer
    path('view-loans/<str:customer_id>/', ViewLoansView.as_view(), name='view_loans'),
]
