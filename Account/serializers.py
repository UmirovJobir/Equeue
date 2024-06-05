import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import *


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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm password')

    class Meta:
        model = User
        fields = ['phone', 'password', 'password2', 'first_name', 'last_name', 'email']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        confirmation_code = '111111' if settings.DEBUG else str(random.randint(100000, 999999))
        expiration_time = timezone.now() + timedelta(minutes=1, seconds=30)
        user = User.objects.create(
            phone=validated_data['phone'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            confirmation_code=confirmation_code,
            expiration_time=expiration_time,
            is_active=False,
        )
        user.set_password(validated_data['password'])
        user.save()
        # Send confirmation_code via SMS here (integration with SMS gateway needed)
        # send_sms(user.phone, confirmation_code)
        return user


class ConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        phone = data.get('phone')
        confirmation_code = data.get('confirmation_code')
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Invalid confirmation code.")

        if user.expiration_time and timezone.now() > user.expiration_time:
            raise serializers.ValidationError("Confirmation code has expired. Please request a new one.")
        
        return data

    def save(self):
        phone = self.validated_data['phone']
        user = User.objects.get(phone=phone)
        user.is_active = True
        user.confirmation_code = None
        user.expiration_time = None
        user.save()
        return user


class ResendConfirmationCodeSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        phone = data.get('phone')
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            try:
                user = User.objects.get(new_phone_temp=phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found.")
        return data

    def save(self):
        phone = self.validated_data['phone']
        user = User.objects.get(phone=phone)
        confirmation_code = '111111' if settings.DEBUG else str(random.randint(100000, 999999))
        expiration_time = timezone.now() + timedelta(minutes=1, seconds=30)
        user.confirmation_code = confirmation_code
        user.expiration_time = expiration_time
        user.save()
        # Send confirmation_code via SMS here (integration with SMS gateway needed)
        # send_sms(user.phone, confirmation_code)
        return user


class UserSerializer(serializers.ModelSerializer):
    # new_phone = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone'] #, 'new_phone']

    # def validate_new_phone(self, value):
    #     if User.objects.filter(phone=value).exists():
    #         raise serializers.ValidationError("This phone number is already in use.")
    #     return value
    
    def validate_phone(self, value):
        if self.instance and value != self.instance.phone:
            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError("This phone number is already in use.")
            confirmation_code = '111111' if settings.DEBUG else str(random.randint(100000, 999999))
            self.instance.confirmation_code = confirmation_code
            self.instance.expiration_time = timezone.now() + timedelta(minutes=1, seconds=30)
            self.instance.new_phone_temp = value
            self.instance.save()
            # Send confirmation_code to the new phone number
            # send_sms(value, confirmation_code)
            raise serializers.ValidationError("A confirmation code has been sent to the new phone number. Please confirm to complete the update.")
        return value

    def update(self, instance, validated_data):
        # new_phone = validated_data.pop('new_phone', None)
        if 'phone' in validated_data:
            validated_data.pop('phone')  # Remove phone from validated data to prevent direct update

        
        # if new_phone:
        #     confirmation_code = '111111' if settings.DEBUG else str(random.randint(100000, 999999))
        #     instance.confirmation_code = confirmation_code
        #     instance.expiration_time = timezone.now() + timedelta(minutes=1, seconds=30)
        #     instance.new_phone_temp = new_phone
        #     instance.save()
        #     # Send confirmation_code to the new phone number
        #     # send_sms(new_phone, confirmation_code)
        #     raise serializers.ValidationError({"message": "A confirmation code has been sent to the new phone number. Please confirm to complete the update."})

        # Update other fields
        for attr, value in validated_data.items():
            print(attr, value)
            setattr(instance, attr, value)
        instance.save()
        return instance


class ConfirmPhoneSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = self.context['request'].user
        confirmation_code = data.get('confirmation_code')
        
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Invalid confirmation code.")
        if user.expiration_time and timezone.now() > user.expiration_time:
            raise serializers.ValidationError("Confirmation code has expired. Please request a new one.")
        
        return data

    def save(self):
        user = self.context['request'].user
        if user.new_phone_temp:
            user.phone = user.new_phone_temp
            user.new_phone_temp = None
        
        user.confirmation_code = None
        user.expiration_time = None
        user.save()
        
        # Update user's token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
                                     
        return user, token