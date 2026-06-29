from multiprocessing.context import AuthenticationError

from rest_framework import serializers
import bcrypt
from rest_framework.response import Response

from accounts.models import UserProfile


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password').encode('utf-8')

        try:
            user = UserProfile.objects.get(email=email)
        except:
            return Response({'error': 'User does not exist'})

        if user is None:
            return Response({'error': 'User does not exist'})

        if not user.is_active:
            return Response({'error': 'User is inactive'})

        if not bcrypt.checkpw(password, user.password.encode('utf-8')):
            return Response({'error': 'Password is incorrect'})

        attrs['user'] = user
        return attrs

