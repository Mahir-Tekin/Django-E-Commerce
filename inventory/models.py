from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.deletion import PROTECT

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    image_url = models.URLField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        """Calculate the average rating of the product"""
        comments = self.comments.all()
        if not comments:
            return 0
        return sum(comment.rating for comment in comments) / comments.count()

    @property
    def total_reviews(self):
        """Get total number of reviews"""
        return self.comments.count()


class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    variation_options = models.ManyToManyField('VariationOption', related_name='product_items')

    def __str__(self):
        return f"{self.product.name} - {self.name or 'Default'}"


class Variation(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class VariationOption(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.variation.name} - {self.name}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=150)
    full_address = models.TextField()
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city}, {self.district}, {self.neighborhood}"


class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(
        max_length=50,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('SHIPPED', 'Shipped'),
            ('DELIVERED', 'Delivered'),
            ('CANCELLED', 'Cancelled')
        ],
        default='PENDING'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    @classmethod
    def create_from_cart(cls, cart, shipping_address):
        """Create an order from cart contents"""
        if not cart.items.exists():
            raise ValueError("Cart is empty")

        with transaction.atomic():
            # Create order
            order = cls.objects.create(
                user=cart.user,
                shipping_address=shipping_address,
                total_amount=cart.total_amount
            )

            # Create order items
            for cart_item in cart.items.all():
                if cart_item.product_item.stock < cart_item.quantity:
                    raise ValueError(f"Insufficient stock for {cart_item.product_item.name}")
                
                OrderItem.objects.create(
                    order=order,
                    product_item=cart_item.product_item,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.product_item.price
                )
                
                # Update stock
                cart_item.product_item.stock -= cart_item.quantity
                cart_item.product_item.save()

            # Clear the cart
            cart.items.all().delete()

            return order


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_item = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_item.name} in Order #{self.order.id}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_item.name} in {self.cart}"

    @property
    def subtotal(self):
        return self.product_item.price * self.quantity
