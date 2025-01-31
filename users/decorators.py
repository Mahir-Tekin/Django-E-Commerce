from graphql import GraphQLError

def login_required(func):

    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Login reqired.")
        return func(root, info, *args, **kwargs)
    return wrapper

def admin_required(func):

    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous or not user.is_staff:
            raise GraphQLError("You do not have permission.")
        return func(root, info, *args, **kwargs)
    return wrapper