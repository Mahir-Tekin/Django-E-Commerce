import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
import inventory.category_schema
import inventory.variation_schema  
import inventory.product_schema
import users.authorization_schema
import inventory.order_schema
import inventory.cart_schema
import inventory.comment_schema
import inventory.address_schema

class Query(graphene.ObjectType):
    # Relay node interface
    node = relay.Node.Field()

    # Category queries
    categories = inventory.category_schema.Query.categories
    category = inventory.category_schema.Query.category
    top_categories = inventory.category_schema.Query.top_categories
    resolve_categories = inventory.category_schema.Query.resolve_categories
    resolve_category = inventory.category_schema.Query.resolve_category
    resolve_top_categories = inventory.category_schema.Query.resolve_top_categories

    # Product queries (Relay style)
    all_products = DjangoFilterConnectionField(inventory.product_schema.ProductNode)
    product = relay.Node.Field(inventory.product_schema.ProductNode)
    all_product_items = DjangoFilterConnectionField(inventory.product_schema.ProductItemNode)
    product_item = relay.Node.Field(inventory.product_schema.ProductItemNode)

    # Variation queries
    all_variations = inventory.variation_schema.Query.all_variations
    variation_by_id = inventory.variation_schema.Query.variation_by_id
    resolve_all_variations = inventory.variation_schema.Query.resolve_all_variations
    resolve_variation_by_id = inventory.variation_schema.Query.resolve_variation_by_id

    # Order queries
    orders = inventory.order_schema.Query.orders
    order = inventory.order_schema.Query.order
    my_orders = inventory.order_schema.Query.my_orders
    resolve_orders = inventory.order_schema.Query.resolve_orders
    resolve_order = inventory.order_schema.Query.resolve_order
    resolve_my_orders = inventory.order_schema.Query.resolve_my_orders

    # Cart queries
    my_cart = inventory.cart_schema.Query.my_cart
    cart_item = inventory.cart_schema.Query.cart_item
    resolve_my_cart = inventory.cart_schema.Query.resolve_my_cart
    resolve_cart_item = inventory.cart_schema.Query.resolve_cart_item

    # Comment queries
    product_comments = inventory.comment_schema.Query.product_comments
    my_comments = inventory.comment_schema.Query.my_comments
    product_rating = inventory.comment_schema.Query.product_rating
    resolve_product_comments = inventory.comment_schema.Query.resolve_product_comments
    resolve_my_comments = inventory.comment_schema.Query.resolve_my_comments
    resolve_product_rating = inventory.comment_schema.Query.resolve_product_rating

    # Address queries
    my_addresses = inventory.address_schema.Query.my_addresses
    address = inventory.address_schema.Query.address
    resolve_my_addresses = inventory.address_schema.Query.resolve_my_addresses
    resolve_address = inventory.address_schema.Query.resolve_address

    # User queries
    me = users.authorization_schema.Query.me
    resolve_me = users.authorization_schema.Query.resolve_me

class Mutation(graphene.ObjectType):
    # Category mutations
    create_category = inventory.category_schema.CreateCategory.Field()
    update_category = inventory.category_schema.UpdateCategory.Field()
    delete_category = inventory.category_schema.DeleteCategory.Field()

    # Product mutations (Relay style)
    create_product = inventory.product_schema.CreateProduct.Field()
    update_product = inventory.product_schema.UpdateProduct.Field()

    # Variation mutations
    create_variation = inventory.variation_schema.CreateVariation.Field()
    update_variation = inventory.variation_schema.UpdateVariation.Field()
    delete_variation = inventory.variation_schema.DeleteVariation.Field()

    # Order mutations
    create_order = inventory.order_schema.CreateOrder.Field()
    update_order_status = inventory.order_schema.UpdateOrderStatus.Field()

    # Cart mutations
    add_to_cart = inventory.cart_schema.AddToCart.Field()
    update_cart_item = inventory.cart_schema.UpdateCartItem.Field()
    remove_from_cart = inventory.cart_schema.RemoveFromCart.Field()
    clear_cart = inventory.cart_schema.ClearCart.Field()
    create_order_from_cart = inventory.cart_schema.CreateOrderFromCart.Field()

    # Comment mutations
    create_comment = inventory.comment_schema.CreateComment.Field()
    update_comment = inventory.comment_schema.UpdateComment.Field()
    delete_comment = inventory.comment_schema.DeleteComment.Field()

    # Address mutations
    create_address = inventory.address_schema.CreateAddress.Field()
    update_address = inventory.address_schema.UpdateAddress.Field()
    delete_address = inventory.address_schema.DeleteAddress.Field()

    # User mutations
    register = users.authorization_schema.RegisterMutation.Field()
    login = users.authorization_schema.LoginMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)