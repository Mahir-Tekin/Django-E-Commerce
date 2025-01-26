# Generated by Django 5.1.5 on 2025-01-22 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_variation_product_productitem_variationoption_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productitem',
            name='variation_options',
            field=models.ManyToManyField(related_name='product_items', to='inventory.variationoption'),
        ),
        migrations.DeleteModel(
            name='ProductItemVariationOption',
        ),
    ]
