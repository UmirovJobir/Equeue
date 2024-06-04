from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from .models import *
from .serializers import *


class BusinessTypeListView(generics.ListAPIView):
    queryset = BusinessType.objects.all()
    serializer_class = BusinessTypeSerializer


class BusinessListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        type_pk = self.kwargs['type_pk']
        return Business.objects.filter(business_type__pk=type_pk)
    
    def perform_create(self, serializer):
        type_pk = self.kwargs['type_pk']
        business_type = BusinessType.objects.get(business_type__pk=type_pk)
        serializer.save(business_type=business_type)


class BusinessDetailView(generics.RetrieveAPIView):
    serializer_class = BusinessSerializer

    def get_object(self):
        type_pk = self.kwargs['type_pk']
        business_pk = self.kwargs['business_pk']
        return get_object_or_404(Business, pk=business_pk, business_type__pk=type_pk)
