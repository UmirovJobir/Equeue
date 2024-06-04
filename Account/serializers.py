from rest_framework import serializers
from django.contrib.auth import authenticate

class AuthTokenSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if not phone:
            raise serializers.ValidationError('Phone number is required.', code='authorization')

        if not password:
            raise serializers.ValidationError('Password is required.', code='authorization')

        user = authenticate(request=self.context.get('request'), phone=phone, password=password)

        if not user:
            raise serializers.ValidationError('Unable to log in with provided credentials.', code='authorization')

        attrs['user'] = user
        return attrs