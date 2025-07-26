from django.urls import path
from .views import (
    CustomerListCreateAPIView,
    CustomerRetrieveUpdateDestroyAPIView,
    RegisterCustomerView
)

urlpatterns = [
    
    path('', CustomerListCreateAPIView.as_view(), name='customer-list-create'),        
    path('<int:id>/', CustomerRetrieveUpdateDestroyAPIView.as_view(), name='customer-detail'),  
    
    # Registration route 
    path('register/', RegisterCustomerView.as_view(), name='register'),              
]
