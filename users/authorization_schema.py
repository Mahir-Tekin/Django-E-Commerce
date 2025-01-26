import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User
from .utils import generate_token
from django.contrib.auth.hashers import make_password, check_password


class UserType(graphene.ObjectType):
    """Kullanıcı bilgilerini tanımlayan GraphQL tipi."""
    id = graphene.Int()
    email = graphene.String()
    username = graphene.String()
   

class UserQuery(graphene.ObjectType):
    """Kullanıcı bilgilerini döndüren sorgu."""
    me = graphene.Field(UserType)

    def resolve_me(self, info):
        user = info.context.user  
        if user.is_anonymous:
            raise GraphQLError("Giriş yapılmamış.")
        return user



class RegisterMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, email, password):
        if User.objects.filter(username=email).exists():
            raise GraphQLError("Bu e-posta adresiyle zaten bir kullanıcı var.")
        user = User.objects.create(
            username=email,
            email=email,
            password=make_password(password)
        )
        return RegisterMutation(success=True, message="Kullanıcı başarıyla oluşturuldu.")

class LoginMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()
    message = graphene.String()

    def mutate(self, info, email, password):
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            raise GraphQLError("Geçersiz e-posta veya şifre.")

        if not check_password(password, user.password):
            raise GraphQLError("Geçersiz e-posta veya şifre.")

        payload = {"user_id": user.id, "email": user.email}
        token = generate_token(payload)
        return LoginMutation(token=token, message="Başarıyla giriş yapıldı.")

class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    login = LoginMutation.Field()

class Query(UserQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(mutation=Mutation,query=Query)
