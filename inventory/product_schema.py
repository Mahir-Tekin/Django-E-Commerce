import graphene
from graphene_django.types import DjangoObjectType
from .models import Product, ProductItem, VariationOption
from django.utils.text import slugify
from datetime import datetime

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "slug", "category", "created_at", "updated_at","items")

class ProductItemType(DjangoObjectType):
    class Meta:
        model = ProductItem
        fields = ("id", "name", "price", "stock", "sku", "product", "variation_options")

class VariationOptionType(DjangoObjectType):
    class Meta:
        model = VariationOption
        fields = ("id", "name", "variation")

class ProductItemInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)
    sku = graphene.String(required=True)
    variation_option_ids = graphene.List(graphene.Int, required=False)  

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        category_id = graphene.Int(required=True)
        items = graphene.List(ProductItemInput, required=True)  

    product = graphene.Field(ProductType)

    def mutate(self, info, name, description, category_id, items):
        if not items:
            raise Exception("At least one product item must be provided.")

        
        product = Product.objects.create(
            name=name,
            description=description,
            category_id=category_id,
            slug=slugify(name),
            created_at=datetime.now()
        )

        
        for item in items:
            product_item = ProductItem.objects.create(
                product=product, name=item.name, price=item.price, stock=item.stock, sku=item.sku
            )

           
            if item.variation_option_ids:
                variation_options = VariationOption.objects.filter(id__in=item.variation_option_ids)
                product_item.variation_options.set(variation_options)

        return CreateProduct(product=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        category_id = graphene.Int(required=False)
        items = graphene.List(ProductItemInput, required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, id, name=None, description=None, category_id=None, items=None):
        try:
            product = Product.objects.get(pk=id)

            if name:
                product.name = name
                product.slug = slugify(name)

            if description:
                product.description = description

            if category_id:
                product.category_id = category_id

            product.save()

            if items:
                for item in items:
                    if "id" in item:
                        product_item = ProductItem.objects.get(pk=item["id"])
                        product_item.name = item.get("name", product_item.name)
                        product_item.price = item.get("price", product_item.price)
                        product_item.stock = item.get("stock", product_item.stock)
                        product_item.sku = item.get("sku", product_item.sku)
                        product_item.save()

                        if "variation_option_ids" in item:
                            variation_options = VariationOption.objects.filter(id__in=item["variation_option_ids"])
                            product_item.variation_options.set(variation_options)
                    else:
                        new_product_item = ProductItem.objects.create(
                            product=product,
                            name=item["name"],
                            price=item["price"],
                            stock=item["stock"],
                            sku=item["sku"]
                        )

                        if "variation_option_ids" in item:
                            variation_options = VariationOption.objects.filter(id__in=item["variation_option_ids"])
                            new_product_item.variation_options.set(variation_options)

            return UpdateProduct(product=product)
        except Product.DoesNotExist:
            raise Exception("Product not found")

class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)
    product_by_id = graphene.Field(ProductType, id=graphene.Int(required=True))

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_product_by_id(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
