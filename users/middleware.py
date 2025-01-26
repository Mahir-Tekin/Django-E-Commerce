import jwt
from django.contrib.auth.models import AnonymousUser, User
from django.utils.deprecation import MiddlewareMixin
from .utils import decode_token

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        authorization_header = request.headers.get('Authorization')  
        if authorization_header:
            try:
                
                token = authorization_header.split(" ")[1]
                decoded_data = decode_token(token)  
                user_id = decoded_data.get("user_id")
                try:
                    request.user = User.objects.get(id=user_id) 
                except User.DoesNotExist:
                    request.user = AnonymousUser()  
            except Exception:
                request.user = AnonymousUser()  
        else:
            request.user = AnonymousUser()  
