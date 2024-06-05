from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', ObtainAuthToken.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/confirm/', RegisterConfirmView.as_view(), name='register-confirm'),
    path('resend-confirmation/', ResendConfirmationCodeView.as_view(), name='resend-confirmation'),
    path('update/', UserDetailView.as_view(), name='user'),
    path('update/confirm/', ConfirmUpdateView.as_view(), name='update-confirm'),
]

