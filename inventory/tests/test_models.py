import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from inventory.tests.factories import (
    CategoryFactory, ProductFactory, ProductItemFactory,
    VariationFactory, VariationOptionFactory, CartFactory,
    CartItemFactory, OrderFactory, OrderItemFactory,
    CommentFactory, AddressFactory
)

pytestmark = pytest.mark.django_db

class TestCategory:
    def test_category_creation(self):
        category = CategoryFactory()
        assert category.name is not None
        assert category.slug is not None
        assert category.image_url is not None

    def test_category_str(self):
        category = CategoryFactory(name="Test Category")
        assert str(category) == "Test Category"

class TestProduct:
    def test_product_creation(self):
        product = ProductFactory()
        assert product.name is not None
        assert product.description is not None
        assert product.slug is not None
        assert product.category is not None
        assert product.is_active is True

    def test_product_str(self):
        product = ProductFactory(name="Test Product")
        assert str(product) == "Test Product"

class TestProductItem:
    def test_product_item_creation(self):
        product_item = ProductItemFactory()
        assert product_item.product is not None
        assert product_item.name is not None
        assert product_item.stock >= 0
        assert product_item.sku is not None
        assert product_item.price > Decimal('0')
        assert product_item.is_active is True

    def test_product_item_str(self):
        product_item = ProductItemFactory(name="Test Item")
        assert str(product_item) == "Test Item"

    def test_product_item_with_variations(self):
        variation = VariationFactory()
        variation_option = VariationOptionFactory(variation=variation)
        product_item = ProductItemFactory(variation_options=[variation_option])
        assert variation_option in product_item.variation_options.all()

class TestVariation:
    def test_variation_creation(self):
        variation = VariationFactory()
        assert variation.name is not None

    def test_variation_str(self):
        variation = VariationFactory(name="Size")
        assert str(variation) == "Size"

class TestVariationOption:
    def test_variation_option_creation(self):
        option = VariationOptionFactory()
        assert option.variation is not None
        assert option.name is not None

    def test_variation_option_str(self):
        variation = VariationFactory(name="Size")
        option = VariationOptionFactory(variation=variation, name="Large")
        assert str(option) == "Size: Large"

class TestCart:
    def test_cart_creation(self):
        cart = CartFactory()
        assert cart.user is not None
        assert cart.items.count() == 0

    def test_cart_with_items(self):
        cart = CartFactory()
        cart_item = CartItemFactory(cart=cart)
        assert cart.items.count() == 1
        assert cart_item in cart.items.all()

class TestCartItem:
    def test_cart_item_creation(self):
        cart_item = CartItemFactory()
        assert cart_item.cart is not None
        assert cart_item.product_item is not None
        assert cart_item.quantity > 0

    def test_cart_item_total_price(self):
        product_item = ProductItemFactory(price=Decimal('10.00'))
        cart_item = CartItemFactory(product_item=product_item, quantity=2)
        assert cart_item.total_price == Decimal('20.00')

class TestOrder:
    def test_order_creation(self):
        order = OrderFactory()
        assert order.user is not None
        assert order.status in ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        assert order.shipping_address is not None
        assert order.total_amount > Decimal('0')

    def test_order_with_items(self):
        order = OrderFactory()
        order_item = OrderItemFactory(order=order)
        assert order.items.count() == 1
        assert order_item in order.items.all()

class TestOrderItem:
    def test_order_item_creation(self):
        order_item = OrderItemFactory()
        assert order_item.order is not None
        assert order_item.product_item is not None
        assert order_item.quantity > 0
        assert order_item.price_at_time > Decimal('0')

    def test_order_item_total_price(self):
        order_item = OrderItemFactory(quantity=2, price_at_time=Decimal('10.00'))
        assert order_item.total_price == Decimal('20.00')

class TestComment:
    def test_comment_creation(self):
        comment = CommentFactory()
        assert comment.user is not None
        assert comment.product is not None
        assert comment.content is not None
        assert 1 <= comment.rating <= 5

    def test_invalid_rating(self):
        with pytest.raises(ValidationError):
            comment = CommentFactory(rating=6)
            comment.full_clean()

class TestAddress:
    def test_address_creation(self):
        address = AddressFactory()
        assert address.user is not None
        assert address.city is not None
        assert address.district is not None
        assert address.neighborhood is not None
        assert address.full_address is not None
        assert address.postal_code is not None

    def test_address_str(self):
        address = AddressFactory(
            city="Istanbul",
            district="Kadikoy",
            neighborhood="Moda"
        )
        expected_str = f"{address.city}, {address.district}, {address.neighborhood}"
        assert str(address) == expected_str 