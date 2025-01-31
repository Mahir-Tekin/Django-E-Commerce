import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from django.db import transaction
from .models import Cart, CartItem, ProductItem, Order, Address

class CartItemType(DjangoObjectType):
    subtotal = graphene.Float()
    
    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'product_item', 'quantity')

class CartType(DjangoObjectType):
    total_amount = graphene.Float()
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'created_at', 'updated_at')

class AddToCart(graphene.Mutation):
    class Arguments:
        product_item_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)

    cart_item = graphene.Field(CartItemType)

    def mutate(self, info, product_item_id, quantity):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to add items to cart.")

        if quantity <= 0:
            raise GraphQLError("Quantity must be greater than 0.")

        try:
            product_item = ProductItem.objects.get(pk=product_item_id)
        except ProductItem.DoesNotExist:
            raise GraphQLError("Product item not found.")

        if not product_item.is_active:
            raise GraphQLError("This product item is not available.")

        if product_item.stock < quantity:
            raise GraphQLError(f"Only {product_item.stock} items available.")

        cart, _ = Cart.objects.get_or_create(user=user)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_item=product_item)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart,
                product_item=product_item,
                quantity=quantity
            )

        return AddToCart(cart_item=cart_item)

class UpdateCartItem(graphene.Mutation):
    class Arguments:
        cart_item_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)

    cart_item = graphene.Field(CartItemType)

    def mutate(self, info, cart_item_id, quantity):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to update cart items.")

        try:
            cart_item = CartItem.objects.get(pk=cart_item_id, cart__user=user)
        except CartItem.DoesNotExist:
            raise GraphQLError("Cart item not found.")

        if quantity <= 0:
            cart_item.delete()
            return UpdateCartItem(cart_item=None)

        if cart_item.product_item.stock < quantity:
            raise GraphQLError(f"Only {cart_item.product_item.stock} items available.")

        cart_item.quantity = quantity
        cart_item.save()
        return UpdateCartItem(cart_item=cart_item)

class RemoveFromCart(graphene.Mutation):
    class Arguments:
        cart_item_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, cart_item_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to remove items from cart.")

        try:
            cart_item = CartItem.objects.get(pk=cart_item_id, cart__user=user)
            cart_item.delete()
            return RemoveFromCart(success=True)
        except CartItem.DoesNotExist:
            raise GraphQLError("Cart item not found.")

class ClearCart(graphene.Mutation):
    success = graphene.Boolean()

    def mutate(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to clear your cart.")

        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
            return ClearCart(success=True)
        except Cart.DoesNotExist:
            return ClearCart(success=True)

class CreateOrderFromCart(graphene.Mutation):
    class Arguments:
        address_id = graphene.Int(required=True)

    order = graphene.Field('inventory.order_schema.OrderType')

    def mutate(self, info, address_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to create an order.")

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise GraphQLError("Cart not found.")

        if not cart.items.exists():
            raise GraphQLError("Your cart is empty.")

        try:
            shipping_address = Address.objects.get(pk=address_id, user=user)
        except Address.DoesNotExist:
            raise GraphQLError("Shipping address not found.")

        try:
            order = Order.create_from_cart(cart, shipping_address)
            return CreateOrderFromCart(order=order)
        except ValueError as e:
            raise GraphQLError(str(e))

class Query(graphene.ObjectType):
    my_cart = graphene.Field(CartType)
    cart_item = graphene.Field(CartItemType, id=graphene.Int(required=True))

    def resolve_my_cart(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to view your cart.")
        
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def resolve_cart_item(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to view cart items.")

        try:
            return CartItem.objects.get(pk=id, cart__user=user)
        except CartItem.DoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    add_to_cart = AddToCart.Field()
    update_cart_item = UpdateCartItem.Field()
    remove_from_cart = RemoveFromCart.Field()
    clear_cart = ClearCart.Field()
    create_order_from_cart = CreateOrderFromCart.Field() 