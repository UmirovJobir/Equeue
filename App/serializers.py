from datetime import datetime
from rest_framework import serializers
from django.utils import timezone
from django.db import IntegrityError
from .models import *

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name']

        
class BusinessImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessImage
        fields = ['id', 'image']


class BusinessSerializer(serializers.ModelSerializer):
    business_type = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )
    new_business_type = serializers.CharField(write_only=True, required=False)
    business_type_id = serializers.IntegerField(write_only=True, required=False)
    images = BusinessImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )


    class Meta:
        model = Business
        fields = ['id', 'name', 'business_type', 'new_business_type', 'business_type_id', 'description', 'logo', 'latitude', 'longitude', 'images', 'image_files']
        extra_kwargs = {
            'creator': {'write_only': True}
        }

    def validate(self, data):
        business_type_id = data.get('business_type_id')
        new_business_type = data.get('new_business_type')

        if not self.instance and not (new_business_type or business_type_id):
            raise serializers.ValidationError("You must provide either 'new_business_type' or 'business_type_id'.")

        if business_type_id:
            try:
                business_type_obj = BusinessType.objects.get(pk=business_type_id)
            except BusinessType.DoesNotExist:
                raise serializers.ValidationError({"business_type_id": f"Business type with the given ID={business_type_id} does not exist."})
        elif new_business_type:
            business_type_obj, created = BusinessType.objects.get_or_create(name=new_business_type)
        elif self.instance:
            business_type_obj = self.instance.business_type

        data['business_type'] = business_type_obj
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['creator'] = request.user
        images_data = request.FILES.getlist('images')

        if not images_data:
            raise serializers.ValidationError({"images": "This field is required."})

        # Remove 'new_business_type' from validated_data
        validated_data.pop('new_business_type', None)
        
        business = super().create(validated_data)

        for image_file in images_data:
            BusinessImage.objects.create(business=business, image=image_file)
        
        return business

    def update(self, instance, validated_data):
        request = self.context.get('request')
        image_files = request.FILES.getlist('images')

        instance = super().update(instance, validated_data)

        instance.images.all().delete()
        if image_files:
            for image_file in image_files:
                BusinessImage.objects.create(business=instance, image=image_file)

        return instance
 
 
class ServiceNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceName
        fields = ['id', 'name', 'business_type']


class ServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.SlugRelatedField(
            slug_field='name', read_only=True
        )
    new_service_name = serializers.CharField(write_only=True, required=False)
    service_name_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Service
        fields = ['id', 'service_name', 'service_name_id', 'new_service_name', 'duration', 'parent']
    
    def validate(self, data):
        business = self.context.get('business')
        service_name_id = data.get('service_name_id')
        new_service_name = data.get('new_service_name')

        if not business:
            raise serializers.ValidationError({"business": "Business is not provided in the context."})

        if service_name_id:
            try:
                service_name_obj = ServiceName.objects.get(pk=service_name_id)
            except ServiceName.DoesNotExist:
                raise serializers.ValidationError({"service_name_id": f"ServiceName with the given ID={service_name_id} does not exist."})
        elif new_service_name:
            service_name_obj, created = ServiceName.objects.get_or_create(name=new_service_name, business_type_id=business.business_type_id)
        else:
            raise serializers.ValidationError({"error": "You must provide either 'new_service_name' or 'service_name_id'."})

        data['service_name'] = service_name_obj
        return data

    def create(self, validated_data):
        business = self.context.get('business')
        validated_data['business'] = business
        
        validated_data.pop('new_service_name', None)
        service_name_obj = validated_data.pop('service_name')
        validated_data['service_name'] = service_name_obj
        
        try:
            service = super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"error": "This service name already exists for this business."})
        
        return service


class EmployeeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRole
        fields = ['id', 'name']


class EmployeeWorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeWorkSchedule
        fields = ['id', 'workday', 'start_time', 'end_time']


class EmployeeSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )
    new_role = serializers.CharField(write_only=True, required=False)
    role_id = serializers.IntegerField(write_only=True, required=False)
    image = serializers.ImageField(required=False)
    work_schedules = EmployeeWorkScheduleSerializer(many=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'role', 'role_id', 'new_role', 'first_name', 'last_name', 'patronymic', 'duration', 'service', 'image', 'phone', 'work_schedules']
    
    def validate(self, data):
        request = self.context.get('request')
        business = self.context.get('business')
        role_id = data.get('role_id')
        new_role = data.get('new_role')

        if not business:
            raise serializers.ValidationError({"business": "Business is not provided in the context."})

        if not self.instance and not (role_id or new_role):
            raise serializers.ValidationError({"error": "You must provide either 'new_role' or 'role_id'."})

        if role_id:
            try:
                role_obj = EmployeeRole.objects.get(pk=role_id)
            except EmployeeRole.DoesNotExist:
                raise serializers.ValidationError({"role_id": f"EmployeeRole with the given ID={role_id} does not exist."})
        elif new_role:
            role_obj, created = EmployeeRole.objects.get_or_create(name=new_role, business_type_id=business.business_type_id)
        elif self.instance:
            role_obj = self.instance.role
        
        data['role'] = role_obj
        return data
    
    def create(self, validated_data):
        business = self.context.get('business')
        validated_data.pop('new_role', None)
        service_data = validated_data.pop('service')
        work_schedules_data = validated_data.pop('work_schedules')
        validated_data['business'] = business
        
        employee = Employee.objects.create(**validated_data)
        
        for work_schedule_data in work_schedules_data:
            EmployeeWorkSchedule.objects.create(employee=employee, **work_schedule_data)
        
        employee.service.set(service_data)
        
        return employee
    
    
    def update(self, instance, validated_data):
        business = self.context.get('business')
        work_schedules_data = validated_data.pop('work_schedules', None)
        service_data = validated_data.pop('service', None)
        validated_data.pop('new_role', None)
        
        instance = super().update(instance, validated_data)

        if work_schedules_data:
            instance.work_schedules.all().delete()
            for work_schedule_data in work_schedules_data:
                EmployeeWorkSchedule.objects.create(employee=instance, **work_schedule_data)

        if service_data is not None:
            instance.service.set(service_data)

        return instance


class OrderSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'business', 'employee', 'service', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['user', 'business', 'employee', 'created_at']

    def get_created_at(self, obj):
        local_created_at = timezone.localtime(obj.created_at)
        return local_created_at.strftime('%Y-%m-%d %H:%M')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        local_start_time = timezone.localtime(instance.start_time)
        local_end_time = timezone.localtime(instance.end_time)
        ret['start_time'] = local_start_time.strftime('%Y-%m-%d %H:%M')
        ret['end_time'] = local_end_time.strftime('%Y-%m-%d %H:%M')
        return ret
    
    def to_internal_value(self, data):
        mutable_data = data.copy()
        if 'start_time' in mutable_data:
            mutable_data['start_time'] = timezone.make_aware(
                datetime.strptime(mutable_data['start_time'], '%Y-%m-%d %H:%M'), timezone.get_current_timezone()
            )
        if 'end_time' in mutable_data:
            mutable_data['end_time'] = timezone.make_aware(
                datetime.strptime(mutable_data['end_time'], '%Y-%m-%d %H:%M'), timezone.get_current_timezone()
            )
        return super().to_internal_value(mutable_data)
    
    def validate(self, data):
        employee = self.context['employee']
        service = data.get('service')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Calculate the order duration
        order_duration = end_time - start_time

        # Get the employee duration if it exists, otherwise use the service duration
        employee_duration = employee.duration
        service_duration = service.duration
        expected_duration = employee_duration if employee_duration else service_duration
        

        # Validate the order duration matches the employee or service duration
        if order_duration != expected_duration:
            raise serializers.ValidationError({
                'end_time': 'The duration between start_time and end_time must match the employee or service duration.'
            })

        # Validate the order times fit within the employee's work schedule
        if not self.employee_works_on_day_and_time(employee, start_time, end_time):
            raise serializers.ValidationError({
                'start_time': 'The order times must fall within the employee\'s work schedule for the selected day.',
                'end_time': 'The order times must fall within the employee\'s work schedule for the selected day.'
            })

        # Check if the employee is available during the specified times
        if not self.is_employee_available(employee, start_time, end_time):
            raise serializers.ValidationError({
                'start_time': 'The employee is not available during the specified times.',
                'end_time': 'The employee is not available during the specified times.'
            })

        return data

    def employee_works_on_day_and_time(self, employee, start_time, end_time):
        workday = start_time.strftime('%a').upper()[:3]
        work_schedules = EmployeeWorkSchedule.objects.filter(employee=employee, workday=workday)
        for schedule in work_schedules:
            if schedule.start_time <= start_time.time() and schedule.end_time >= end_time.time():
                return True
        return False

    def is_employee_available(self, employee, start_time, end_time):
        return not Order.objects.filter(
            employee=employee,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
    
    def create(self, validated_data):
        business = self.context.get('business')
        employee = self.context.get('employee')
        user = self.context.get('user')
    
        order = Order.objects.create(
            user=user, business=business, employee=employee, **validated_data
        )
        return order


class AvailableTimeSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['start_time'] = instance['start_time'].strftime('%Y-%m-%d %H:%M')
        ret['end_time'] = instance['end_time'].strftime('%Y-%m-%d %H:%M')
        return ret