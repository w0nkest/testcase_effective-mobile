import jwt
import uuid
import datetime as dt
from django.conf import settings

from log_acc.models import ExpiredToken

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME = dt.timedelta(minutes=5)
REFRESH_TOKEN_LIFETIME = dt.timedelta(days=1)

def create_access_token(user_id):
    jti = str(uuid.uuid4())

    payload = {
        'user_id': user_id,
        'jti': jti,
        'type': 'access',
        'exp': dt.datetime.now(dt.UTC) + ACCESS_TOKEN_LIFETIME,
        'iat': dt.datetime.now(dt.UTC),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token, jti, payload['exp']


def create_refresh_token(user_id, token_family=None):
    refresh_jti = str(uuid.uuid4())
    if token_family is None:
        token_family = str(uuid.uuid4())  # новое семейство
    payload = {
        'user_id': user_id,
        'jti': refresh_jti,
        'type': 'refresh',
        'token_family': token_family,
        'exp': dt.datetime.now(dt.UTC) + REFRESH_TOKEN_LIFETIME,
        'iat': dt.datetime.now(dt.UTC),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, refresh_jti, payload['exp'], token_family


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Token expired')

    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token')

def is_token_expired(jti):
    return ExpiredToken.objects.filter(jti=jti).exists()