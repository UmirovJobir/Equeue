from django.utils import timezone
from datetime import datetime, timedelta
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
    
    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     print(self.request.data)
    #     business_pk = self.kwargs['business_pk']
    #     try:
    #         business = Business.objects.get(pk=business_pk)
    #     except Business.DoesNotExist:
    #         raise serializers.ValidationError({"business": f"Business with ID {business_pk} does not exist."})
    #     context['business'] = business
    #     return context


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
    permission_classes = [permissions.IsAuthenticated, IsBusinessCreatorOrCreateOnly]

    def get_queryset(self):
        employee_pk = self.kwargs['employee_pk']
        today = timezone.now().date()
        return Order.objects.filter(employee__pk=employee_pk, start_time__date__gte=today)
    
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
     

# class AvailableTimeListView(views.APIView):
#     def get(self, request, *args, **kwargs):
#         employee_pk = self.kwargs['employee_pk']
#         try:
#             employee = Employee.objects.get(pk=employee_pk)
#         except Employee.DoesNotExist:
#             raise serializers.ValidationError({"employee": "Employee does not exist."})
        
#         today = timezone.now().date()
#         orders = Order.objects.filter(employee=employee, start_time__date__gte=today)
        
#         serializers = AvailableTimesSerializer(orders, many=True)
        
#         return response.Response(serializers.data)

from rest_framework.response import Response

class AvailableTimeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AvailableTimeSerializer

    def get(self, request, *args, **kwargs):
        employee_pk = self.kwargs['employee_pk']
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({"detail": "Please provide start_date and end_date in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(pk=employee_pk)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        available_times = self.calculate_available_times(employee, start_date, end_date)

        serializer = self.get_serializer(available_times, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def calculate_available_times(self, employee, start_date, end_date):
        available_times = []
        delta = timedelta(days=1)

        while start_date <= end_date:
            work_schedules = EmployeeWorkSchedule.objects.filter(employee=employee, workday=start_date.strftime('%a').upper()[:3])
            orders = Order.objects.filter(employee=employee, start_time__date=start_date)

            for schedule in work_schedules:
                start_of_day = datetime.combine(start_date, schedule.start_time)
                end_of_day = datetime.combine(start_date, schedule.end_time)

                current_time = start_of_day

                while current_time < end_of_day:
                    next_time = current_time + timedelta(minutes=30)
                    if not orders.filter(start_time__lt=next_time, end_time__gt=current_time).exists():
                        available_times.append({
                            "start_time": current_time,
                            "end_time": next_time
                        })
                    current_time = next_time

            start_date += delta

        return available_times