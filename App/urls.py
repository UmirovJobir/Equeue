from django.urls import path
from .views import *


urlpatterns = [
    path('type/', BusinessTypeListView.as_view(), name='businesstype'),
    path('business/', BusinessListCreateView.as_view(), name='business'),
    path('business/<int:business_pk>/', BusinessDetailView.as_view(), name='business-detail'),
    path('business/<int:business_pk>/service/', ServiceListCreateView.as_view(), name='service'),
    path('business/<int:business_pk>/service/<int:service_pk>/', SubServiceListAPIView.as_view(), name='subservice'),
    path('business/<int:business_pk>/service/<int:service_pk>/employee/', EmployeeListCreateView.as_view(), name='employee'),
    path('business/<int:business_pk>/service/<int:service_pk>/employee/<int:employee_pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employee/<int:employee_pk>/order/', OrderListCreateView.as_view(), name='order'),
    path('employee/<int:employee_pk>/evailabe/', AvailableTimeView.as_view(), name='available'),
]