from rest_framework import serializers
from .models import *

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name']

class BusinessSerializer(serializers.ModelSerializer):
    business_type = serializers.SlugRelatedField(queryset=BusinessType.objects.all(), slug_field='name')
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'business_type', 'description', 'logo', 'latitude', 'longitude']
        