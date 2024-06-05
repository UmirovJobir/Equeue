from rest_framework import serializers
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
    business_type = serializers.SlugRelatedField(queryset=BusinessType.objects.all(), slug_field='name', required=False)
    business_type_id = serializers.IntegerField(write_only=True, required=False)
    images = BusinessImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'business_type', 'business_type_id', 'description', 'logo', 'latitude', 'longitude', 'images', 'image_files']
        extra_kwargs = {
            'creater': {'write_only': True}
        }
        
    def to_internal_value(self, data):
        business_type_name = data.get('business_type')
        if business_type_name:
            business_type, created = BusinessType.objects.get_or_create(name=business_type_name)
            data['business_type'] = business_type.name
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['creater'] = request.user
        
        business_type_id = validated_data.pop('business_type_id', None)
        business_type_name = validated_data.pop('business_type', None)
        image_files = validated_data.pop('image_files', [])
        
        if business_type_id:
            try:
                business_type = BusinessType.objects.get(pk=business_type_id)
            except BusinessType.DoesNotExist:
                raise serializers.ValidationError({"business_type_id": f"Business type with the given ID={business_type_id} does not exist."})
        elif business_type_name:
            business_type, created = BusinessType.objects.get_or_create(name=business_type_name)
        else:
            raise serializers.ValidationError("You must provide either 'business_type' or 'business_type_id'.")

        validated_data['business_type'] = business_type
        business = super().create(validated_data)
        
        for image_file in image_files:
            BusinessImage.objects.create(business=business, image=image_file)
        
        return business
 
 
class ServiceNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceName
        fields = ['id', 'name', 'business_type']


class ServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.SlugRelatedField(
            queryset=ServiceName.objects.all(), slug_field='name', required=False, allow_null=True
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
    