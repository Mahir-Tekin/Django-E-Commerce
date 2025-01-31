import pytest
from graphene.test import Client
from django.test import RequestFactory
from ecommerce.schema import schema
from inventory.tests.factories import (
    CategoryFactory, ProductFactory, ProductItemFactory,
    UserFactory, CartFactory, CartItemFactory,
    OrderFactory, CommentFactory
)

pytestmark = pytest.mark.django_db

@pytest.fixture
def client():
    return Client(schema)

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def user():
    return UserFactory()

class TestQueries:
    def test_get_categories(self, client):
        CategoryFactory.create_batch(3)
        query = '''
            query {
                categories {
                    id
                    name
                    slug
                    imageUrl
                }
            }
        '''
        result = client.execute(query)
        assert 'errors' not in result
        assert len(result['data']['categories']) == 3

    def test_get_products(self, client):
        ProductFactory.create_batch(3)
        query = '''
            query {
                products {
                    id
                    name
                    description
                    slug
                    category {
                        name
                    }
                }
            }
        '''
        result = client.execute(query)
        assert 'errors' not in result
        assert len(result['data']['products']) == 3

    def test_get_product_by_slug(self, client):
        product = ProductFactory(slug='test-product')
        query = '''
            query {
                product(slug: "test-product") {
                    id
                    name
                    description
                }
            }
        '''
        result = client.execute(query)
        assert 'errors' not in result
        assert result['data']['product']['name'] == product.name

    def test_get_product_items(self, client):
        ProductItemFactory.create_batch(3)
        query = '''
            query {
                productItems {
                    id
                    name
                    sku
                    price
                    stock
                }
            }
        '''
        result = client.execute(query)
        assert 'errors' not in result
        assert len(result['data']['productItems']) == 3

class TestMutations:
    def test_create_cart(self, client, request_factory, user):
        request = request_factory.post('/')
        request.user = user
        
        mutation = '''
            mutation {
                createCart {
                    cart {
                        id
                        user {
                            username
                        }
                    }
                }
            }
        '''
        result = client.execute(mutation, context=request)
        assert 'errors' not in result
        assert result['data']['createCart']['cart']['user']['username'] == user.username

    def test_add_to_cart(self, client, request_factory, user):
        cart = CartFactory(user=user)
        product_item = ProductItemFactory()
        request = request_factory.post('/')
        request.user = user

        mutation = f'''
            mutation {{
                addToCart(input: {{
                    productItemId: "{product_item.id}",
                    quantity: 2
                }}) {{
                    cartItem {{
                        id
                        quantity
                        productItem {{
                            id
                        }}
                    }}
                }}
            }}
        '''
        result = client.execute(mutation, context=request)
        assert 'errors' not in result
        assert result['data']['addToCart']['cartItem']['quantity'] == 2

    def test_create_order(self, client, request_factory, user):
        cart = CartFactory(user=user)
        cart_item = CartItemFactory(cart=cart)
        request = request_factory.post('/')
        request.user = user

        mutation = '''
            mutation {
                createOrder(input: {
                    shippingAddress: {
                        city: "Istanbul"
                        district: "Kadikoy"
                        neighborhood: "Moda"
                        fullAddress: "Test Address"
                        postalCode: "34710"
                    }
                }) {
                    order {
                        id
                        status
                        totalAmount
                    }
                }
            }
        '''
        result = client.execute(mutation, context=request)
        assert 'errors' not in result
        assert result['data']['createOrder']['order']['status'] == 'PENDING'

    def test_create_comment(self, client, request_factory, user):
        product = ProductFactory()
        request = request_factory.post('/')
        request.user = user

        mutation = f'''
            mutation {{
                createComment(input: {{
                    productId: "{product.id}",
                    content: "Great product!",
                    rating: 5
                }}) {{
                    comment {{
                        id
                        content
                        rating
                        user {{
                            username
                        }}
                    }}
                }}
            }}
        '''
        result = client.execute(mutation, context=request)
        assert 'errors' not in result
        assert result['data']['createComment']['comment']['content'] == "Great product!"
        assert result['data']['createComment']['comment']['rating'] == 5 