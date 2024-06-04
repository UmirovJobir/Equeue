from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AuthTokenSerializer


class ObtainAuthToken(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})