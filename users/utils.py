import jwt
from datetime import datetime, timedelta
from django.conf import settings

# JWT ile ilgili sabitler (SECRET ve EXPIRATION TIME)
SECRET_KEY = settings.SECRET_KEY  # Django'nun settings dosyasındaki SECRET_KEY'i kullanıyoruz.
ALGORITHM = "HS256"  # Kullanılacak algoritma
TOKEN_EXPIRATION_MINUTES = 60  # Token'ın geçerlilik süresi (örnek: 60 dakika)

def generate_token(payload):

    payload["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)  # Token süresi
    payload["iat"] = datetime.utcnow()  # Token'ın oluşturulma zamanı
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token is expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid Token.")

