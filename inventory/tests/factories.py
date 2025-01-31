import factory
from django.contrib.auth.models import User
from inventory.models import (
    Category, Product, ProductItem, Variation, 
    VariationOption, Cart, CartItem, Order, 
    OrderItem, Comment, Address
)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.LazyAttribute(lambda obj: f'category-{obj.name.lower().replace(" ", "-")}')
    image_url = factory.LazyAttribute(lambda obj: f'https://example.com/images/{obj.slug}.jpg')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f'Product {n}')
    description = factory.Faker('paragraph')
    slug = factory.LazyAttribute(lambda obj: f'product-{obj.name.lower().replace(" ", "-")}')
    is_active = True

class VariationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Variation

    name = factory.Sequence(lambda n: f'Variation {n}')

class VariationOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VariationOption

    variation = factory.SubFactory(VariationFactory)
    name = factory.Sequence(lambda n: f'Option {n}')

class ProductItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductItem

    product = factory.SubFactory(ProductFactory)
    name = factory.Sequence(lambda n: f'Item {n}')
    stock = factory.Faker('random_int', min=0, max=100)
    sku = factory.Sequence(lambda n: f'SKU-{n:05d}')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    is_active = True

    @factory.post_generation
    def variation_options(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for option in extracted:
                self.variation_options.add(option)

class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    user = factory.SubFactory(UserFactory)
    city = factory.Faker('city')
    district = factory.Faker('city_suffix')
    neighborhood = factory.Faker('street_name')
    full_address = factory.Faker('address')
    postal_code = factory.Faker('postcode')

class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)

class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product_item = factory.SubFactory(ProductItemFactory)
    quantity = factory.Faker('random_int', min=1, max=5)

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    status = factory.Iterator(['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED'])
    shipping_address = factory.SubFactory(AddressFactory)
    total_amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)

class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product_item = factory.SubFactory(ProductItemFactory)
    quantity = factory.Faker('random_int', min=1, max=5)
    price_at_time = factory.LazyAttribute(lambda obj: obj.product_item.price)

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    content = factory.Faker('paragraph')
    rating = factory.Faker('random_int', min=1, max=5) 