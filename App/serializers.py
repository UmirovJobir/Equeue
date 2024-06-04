from rest_framework import serializers
from .models import *

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name']

class BusinessSerializer(serializers.ModelSerializer):
    business_type = serializers.SlugRelatedField(queryset=BusinessType.objects.all(), slug_field='name', required=False)
    business_type_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'business_type', 'business_type_id', 'description', 'logo', 'latitude', 'longitude']
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
        return super().create(validated_data)
        