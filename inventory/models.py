from django.db import models

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
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name


class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')  
    name = models.CharField(max_length=255, blank=True, null=True)  
    stock = models.PositiveIntegerField(default=0)  
    sku = models.CharField(max_length=100, unique=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    variation_options = models.ManyToManyField('VariationOption', related_name='product_items')  # Many-to-Many ilişkisi

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
