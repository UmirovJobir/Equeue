from django.urls import path
from .views import *


urlpatterns = [
    path('type/', BusinessTypeListView.as_view(), name='businesstype'),
    path('business/', BusinessListCreateView.as_view(), name='business'),
    path('business/<int:business_pk>/', BusinessDetailView.as_view(), name='business'),
    path('business/<int:business_pk>/service/', ServiceListCreateView.as_view(), name='service'),
    path('business/<int:business_pk>/service/<int:service_pk>/', SubServiceListAPIView.as_view(), name='subservice'),
]