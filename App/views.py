# from django.utils import timezone
from datetime import datetime, timedelta, timezone
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers, response, views, status

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


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessSerializer

    def get_object(self):
        business_pk = self.kwargs['business_pk']
        return get_object_or_404(Business, pk=business_pk)


class BusinessOrdersListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsBusinessCreator]

    def get_queryset(self):
        employee_pk = self.kwargs['employee_pk']
        date_str = self.request.query_params.get('date')
        
        if date_str:
            try:
                date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError({"date": "Date format should be YYYY-MM-DD"})
        else:
            date = timezone.now().date()
            
        return Order.objects.filter(
            employee__pk=employee_pk,
            start_time__date=date
        )


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


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        employee_pk = self.kwargs['employee_pk']
        date_str = self.request.query_params.get('date')
        
        if date_str:
            try:
                date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError({"date": "Date format should be YYYY-MM-DD"})
        else:
            date = timezone.now().date()
            
        return Order.objects.filter(
            user=self.request.user,
            employee__pk=employee_pk,
            start_time__date=date,
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        employee_pk = self.kwargs['employee_pk']
        try:
            employee = Employee.objects.get(pk=employee_pk)
            business = employee.business
        except Employee.DoesNotExist:
            raise serializers.ValidationError({"employee": "Employee does not exist."})
        context['business'] = business
        context['employee'] = employee
        context['user'] = user
        return context


class AvailableTimeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AvailableTimeSerializer

    def get(self, request, *args, **kwargs):
        employee_pk = self.kwargs['employee_pk']
        service_pk = self.kwargs['service_pk']

        today = datetime.now()

        date = request.query_params.get('date')
        
        if date is None:
            date = today.date().strftime('%Y-%m-%d')
        elif date < today.date().strftime('%Y-%m-%d'):
            return response.Response({"detail": "Date must be today or in the future."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return response.Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(pk=employee_pk)
        except Employee.DoesNotExist:
            return response.Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            service = Service.objects.get(pk=service_pk)
        except Service.DoesNotExist:
            return response.Response({"detail": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        available_times = self.calculate_available_times(employee, service, date)

        serializer = self.get_serializer(available_times, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


    def calculate_available_times(self, employee, service, date):
        available_times = []
        
        employee_duration = employee.duration
        service_duration = service.duration
        expected_duration = employee_duration if employee_duration else service_duration
        
        work_schedules = EmployeeWorkSchedule.objects.filter(employee=employee, workday=date.strftime('%a').upper()[:3])
        orders = Order.objects.filter(employee=employee, start_time__date=date, end_time__date=date)
        
        for schedule in work_schedules:
            start_of_day =  timezone.make_aware(datetime.combine(date, schedule.start_time), timezone.get_current_timezone())            
            end_of_day =  timezone.make_aware(datetime.combine(date, schedule.end_time), timezone.get_current_timezone())

            current_time = start_of_day

            while current_time < end_of_day:
                next_time = current_time + timedelta(seconds=expected_duration.total_seconds())
                if not orders.filter(start_time__lt=next_time, end_time__gt=current_time).exists():
                    available_times.append({
                        "start_time": current_time.strftime('%H:%M'),
                        "end_time": next_time.strftime('%H:%M')
                    })
                current_time = next_time

        return available_times


