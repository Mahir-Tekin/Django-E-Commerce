import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from .models import Address

class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        fields = ('id', 'user', 'city', 'district', 'neighborhood', 'full_address', 'postal_code', 'created_at', 'updated_at')

class CreateAddress(graphene.Mutation):
    class Arguments:
        city = graphene.String(required=True)
        district = graphene.String(required=True)
        neighborhood = graphene.String(required=True)
        full_address = graphene.String(required=True)
        postal_code = graphene.String(required=True)

    address = graphene.Field(AddressType)

    def mutate(self, info, city, district, neighborhood, full_address, postal_code):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to add an address.")

        address = Address.objects.create(
            user=user,
            city=city,
            district=district,
            neighborhood=neighborhood,
            full_address=full_address,
            postal_code=postal_code
        )

        return CreateAddress(address=address)

class UpdateAddress(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        city = graphene.String()
        district = graphene.String()
        neighborhood = graphene.String()
        full_address = graphene.String()
        postal_code = graphene.String()

    address = graphene.Field(AddressType)

    def mutate(self, info, id, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to update an address.")

        try:
            address = Address.objects.get(pk=id, user=user)
        except Address.DoesNotExist:
            raise GraphQLError("Address not found or you don't have permission to update it.")

        for field, value in kwargs.items():
            if value is not None:
                setattr(address, field, value)

        address.save()
        return UpdateAddress(address=address)

class DeleteAddress(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to delete an address.")

        try:
            address = Address.objects.get(pk=id, user=user)
            # Check if address is used in any active orders
            if address.orders.filter(status__in=['PENDING', 'PROCESSING', 'SHIPPED']).exists():
                raise GraphQLError("Cannot delete address that is used in active orders.")
            address.delete()
            return DeleteAddress(success=True)
        except Address.DoesNotExist:
            raise GraphQLError("Address not found or you don't have permission to delete it.")

class Query(graphene.ObjectType):
    my_addresses = graphene.List(AddressType)
    address = graphene.Field(AddressType, id=graphene.Int(required=True))

    def resolve_my_addresses(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to view your addresses.")
        return Address.objects.filter(user=user).order_by('-created_at')

    def resolve_address(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to view address details.")

        try:
            return Address.objects.get(pk=id, user=user)
        except Address.DoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    create_address = CreateAddress.Field()
    update_address = UpdateAddress.Field()
    delete_address = DeleteAddress.Field() 