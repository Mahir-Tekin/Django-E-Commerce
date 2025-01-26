from graphql import GraphQLError

def login_required(func):
    """
    Kullanıcının giriş yapmış olmasını kontrol eder.
    Eğer kullanıcı giriş yapmamışsa, hata fırlatır.
    """
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Bu işlemi gerçekleştirmek için giriş yapmalısınız.")
        return func(root, info, *args, **kwargs)
    return wrapper

def admin_required(func):
    """
    Kullanıcının admin yetkisine sahip olup olmadığını kontrol eder.
    """
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous or not user.is_staff:
            raise GraphQLError("Bu işlemi gerçekleştirmek için admin yetkisine sahip olmalısınız.")
        return func(root, info, *args, **kwargs)
    return wrapper