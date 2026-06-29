import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from accounts.models import UserProfile
from usersproj.jwt_utils import decode_token, is_token_expired

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.COOKIES.get('access_token')

        if not token:
            return None

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        if payload.get('type') != 'access':
            raise AuthenticationFailed('Invalid token type')

        jti = payload.get('jti')
        if jti and is_token_expired(jti):
            raise AuthenticationFailed('Token revoked')

        user_id = payload.get('user_id')
        try:
            user = UserProfile.objects.get(id=user_id, is_active=True)
        except UserProfile.DoesNotExist:
            raise AuthenticationFailed('User not found or inactive')

        return user, token