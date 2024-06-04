from django.urls import path
from .views import *


urlpatterns = [
    path('type/', BusinessTypeListView.as_view(), name='businesstype'),
    path('business/', BusinessListCreateView.as_view(), name='business'),
    path('type/<int:type_pk>/business/<int:business_pk>/', BusinessDetailView.as_view(), name='business'),
]