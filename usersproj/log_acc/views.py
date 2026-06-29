import datetime as dt

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .authentications import JWTAuthentication

from .models import ExpiredToken, RefreshToken
from .serializers import LoginSerializer
from usersproj.jwt_utils import create_access_token, decode_token, create_refresh_token, ACCESS_TOKEN_LIFETIME


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh_token_str, refresh_jti, refresh_exp, token_family = create_refresh_token(user.id)

        RefreshToken.objects.create(
            jti=refresh_jti,
            user=user,
            token_family=token_family,
            expires_at=refresh_exp
        )

        access_token = create_access_token(user.id)

        response = Response({
            'refresh_token': refresh_token_str,
            'expires_in': int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            'token_type': 'Bearer'
        }, status=200)

        response.set_cookie(
            key='access_token',
            value=access_token[0],
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=int(ACCESS_TOKEN_LIFETIME.total_seconds())
        )

        return response


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return Response({'error': 'No access token in cookies'}, status=400)

        try:
            payload = decode_token(token)
            jti = payload.get('jti')
            exp = dt.datetime.fromtimestamp(payload['exp'], dt.UTC)
        except:
            return Response({'error': 'Invalid token'}, status=400)

        ExpiredToken.objects.create(jti=jti, expires=exp)

        response = Response({'detail': 'Successfully logged out'}, status=200)
        response.delete_cookie('access_token')

        return Response({'detail': 'Successfully logged out'}, status=200)

