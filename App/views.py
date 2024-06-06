from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers

from .models import *
from .serializers import *
from .permissions import *


class BusinessTypeListView(generics.ListAPIView):
    queryset = BusinessType.objects.all()
    serializer_class = BusinessTypeSerializer


class BusinessListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        type_id = self.request.query_params.get('type_id')
        if type_id:
            return Business.objects.filter(business_type__pk=type_id)
        else:
            return Business.objects.all()
    

class BusinessDetailView(generics.RetrieveAPIView):
    serializer_class = BusinessSerializer

    def get_object(self):
        business_pk = self.kwargs['business_pk']
        return get_object_or_404(Business, pk=business_pk)


class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsBusinessCreatorOrReadOnly]

    def get_queryset(self):
        business_pk = self.kwargs['business_pk']
        return Service.objects.filter(business__pk=business_pk, parent__isnull=True)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        business_pk = self.kwargs['business_pk']
        try:
            business = Business.objects.get(pk=business_pk)
        except Business.DoesNotExist:
            raise serializers.ValidationError({"business": f"Business with ID {business_pk} does not exist."})
        context['business'] = business
        return context
    


class SubServiceListAPIView(generics.ListAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        business_pk = self.kwargs['business_pk']
        service_pk = self.kwargs['service_pk']
        services = Service.objects.filter(business_id=business_pk, parent_id=service_pk)
        if not services.exists():
            raise serializers.ValidationError({"service": f"Service with ID {service_pk} does not have subservices."})
        return services


class EmployeeListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsBusinessCreatorOrReadOnly]

    def get_queryset(self):
        business_pk = self.kwargs['business_pk']
        return Employee.objects.filter(business__pk=business_pk)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        business_pk = self.kwargs['business_pk']
        try:
            business = Business.objects.get(pk=business_pk)
        except Business.DoesNotExist:
            raise serializers.ValidationError({"business": f"Business with ID {business_pk} does not exist."})
        context['business'] = business
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        business = self.get_serializer_context()['business']
        serializer.save(business=business)


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsBusinessCreatorOrReadOnly]

    def get_object(self):
        business_pk = self.kwargs['business_pk']
        employee_pk = self.kwargs['employee_pk']
        return get_object_or_404(Employee, business__pk=business_pk, pk=employee_pk)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        business_pk = self.kwargs['business_pk']
        try:
            business = Business.objects.get(pk=business_pk)
        except Business.DoesNotExist:
            raise serializers.ValidationError({"business": f"Business with ID {business_pk} does not exist."})
        context['business'] = business
        return context