import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from django.db import transaction
from .models import Order, OrderItem, ProductItem

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'total_amount', 'shipping_address', 'created_at', 'updated_at', 'items')

class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product_item', 'quantity', 'price_at_time')

class OrderItemInput(graphene.InputObjectType):
    product_item_id = graphene.Int(required=True)
    quantity = graphene.Int(required=True)

class CreateOrder(graphene.Mutation):
    class Arguments:
        items = graphene.List(OrderItemInput, required=True)
        shipping_address = graphene.String(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, items, shipping_address):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to create an order.")

        if not items:
            raise GraphQLError("Order must contain at least one item.")

        with transaction.atomic():
            # Calculate total amount and validate stock
            total_amount = 0
            order_items_data = []
            
            for item_input in items:
                try:
                    product_item = ProductItem.objects.get(pk=item_input.product_item_id)
                except ProductItem.DoesNotExist:
                    raise GraphQLError(f"Product item {item_input.product_item_id} not found.")

                if product_item.stock < item_input.quantity:
                    raise GraphQLError(f"Insufficient stock for {product_item.name}")

                item_total = product_item.price * item_input.quantity
                total_amount += item_total
                
                order_items_data.append({
                    'product_item': product_item,
                    'quantity': item_input.quantity,
                    'price_at_time': product_item.price
                })

            # Create order
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                shipping_address=shipping_address
            )

            # Create order items and update stock
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product_item=item_data['product_item'],
                    quantity=item_data['quantity'],
                    price_at_time=item_data['price_at_time']
                )
                
                # Update stock
                item_data['product_item'].stock -= item_data['quantity']
                item_data['product_item'].save()

            return CreateOrder(order=order)

class UpdateOrderStatus(graphene.Mutation):
    class Arguments:
        order_id = graphene.Int(required=True)
        status = graphene.String(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, order_id, status):
        user = info.context.user
        if not user.is_staff:
            raise GraphQLError("Only staff members can update order status.")

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise GraphQLError("Order not found.")

        if status not in [s[0] for s in Order._meta.get_field('status').choices]:
            raise GraphQLError("Invalid status.")

        order.status = status
        order.save()
        return UpdateOrderStatus(order=order)

class Query(graphene.ObjectType):
    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.Int(required=True))
    my_orders = graphene.List(OrderType)

    def resolve_orders(self, info):
        user = info.context.user
        if not user.is_staff:
            raise GraphQLError("Only staff members can view all orders.")
        return Order.objects.all().order_by('-created_at')

    def resolve_order(self, info, id):
        user = info.context.user
        try:
            order = Order.objects.get(pk=id)
            if not user.is_staff and order.user != user:
                raise GraphQLError("You don't have permission to view this order.")
            return order
        except Order.DoesNotExist:
            return None

    def resolve_my_orders(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to view your orders.")
        return Order.objects.filter(user=user).order_by('-created_at')

class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()
    update_order_status = UpdateOrderStatus.Field() 