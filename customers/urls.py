from django.urls import path
from .views import (
    CustomerListCreateAPIView,
    CustomerRetrieveUpdateDestroyAPIView,
    RegisterCustomerView
)

urlpatterns = [
    
    path('', CustomerListCreateAPIView.as_view(), name='customer-list-create'),          # Full URL: /api/customers/
    path('<int:id>/', CustomerRetrieveUpdateDestroyAPIView.as_view(), name='customer-detail'),  # Full URL: /api/customers/<id>/
    
    # Registration route (keep as is)
    path('register/', RegisterCustomerView.as_view(), name='register'),                 # Full URL: /api/customers/register/
]
