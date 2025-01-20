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
