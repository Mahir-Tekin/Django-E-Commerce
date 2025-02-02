import pytest
from django.contrib.auth.models import User, AnonymousUser
from graphene.test import Client
from django.test import RequestFactory
from users.authorization_schema import schema
from inventory.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

@pytest.fixture
def client():
    return Client(schema)

@pytest.fixture
def request_factory():
    return RequestFactory()

class TestAuthMutations:
    def test_register_user(self, client):
        mutation = '''
            mutation {
                register(email: "test@example.com", password: "testpass123") {
                    success
                    message
                }
            }
        '''
        result = client.execute(mutation)
        assert 'errors' not in result
        assert result['data']['register']['success'] is True

    def test_register_user_duplicate_email(self, client):
        # Create a user first
        UserFactory(username='test@example.com', email='test@example.com')

        mutation = '''
            mutation {
                register(email: "test@example.com", password: "testpass123") {
                    success
                    message
                }
            }
        '''
        result = client.execute(mutation)
        assert 'errors' in result
        assert 'Bu e-posta adresiyle zaten bir kullanıcı var' in str(result['errors'])

    def test_login_user(self, client):
        # Create a user first
        user = UserFactory(username='test@example.com', email='test@example.com')
        user.set_password('testpass123')
        user.save()

        mutation = '''
            mutation {
                login(email: "test@example.com", password: "testpass123") {
                    token
                    message
                }
            }
        '''
        result = client.execute(mutation)
        assert 'errors' not in result
        assert result['data']['login']['token'] is not None
        assert result['data']['login']['message'] == "Başarıyla giriş yapıldı."

    def test_login_user_invalid_credentials(self, client):
        mutation = '''
            mutation {
                login(email: "nonexistent@example.com", password: "wrongpass") {
                    token
                    message
                }
            }
        '''
        result = client.execute(mutation)
        assert 'errors' in result
        assert 'Geçersiz e-posta veya şifre' in str(result['errors'])

    def test_me_query_authenticated(self, client, request_factory):
        # Create and login user first
        user = UserFactory(username='test@example.com', email='test@example.com')
        user.set_password('testpass123')
        user.save()

        # Create request with authenticated user
        request = request_factory.get('/')
        request.user = user

        query = '''
            query {
                me {
                    id
                    email
                    username
                }
            }
        '''
        result = client.execute(query, context=request)
        assert 'errors' not in result
        assert result['data']['me']['email'] == 'test@example.com'

    def test_me_query_unauthenticated(self, client, request_factory):
        # Create request with anonymous user
        request = request_factory.get('/')
        request.user = AnonymousUser()

        query = '''
            query {
                me {
                    id
                    email
                    username
                }
            }
        '''
        result = client.execute(query, context=request)
        assert 'errors' in result
        assert 'Giriş yapılmamış' in str(result['errors']) 