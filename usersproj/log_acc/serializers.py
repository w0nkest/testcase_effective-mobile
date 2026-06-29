from multiprocessing.context import AuthenticationError

from rest_framework import serializers
import bcrypt

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
            raise AuthenticationError('User does not exist')

        if user is None:
            raise AuthenticationError('User does not exist')

        if not user.is_active:
            raise AuthenticationError('User is inactive')

        if not bcrypt.checkpw(password, user.password.encode('utf-8')):
            raise AuthenticationError('Password is incorrect')

        attrs['user'] = user
        return attrs

