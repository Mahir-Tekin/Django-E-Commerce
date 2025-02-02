import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import django_filters

from django.utils.text import slugify
from django.utils import timezone

from users.decorators import login_required, admin_required
from .models import Product, ProductItem, VariationOption


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product

        fields = {
            "name": ["exact", "icontains"],
            "is_active": ["exact"],
            "category__name": ["icontains", "exact"],
        }

class ProductItemFilter(django_filters.FilterSet):
    class Meta:
        model = ProductItem
        fields = {
            "name": ["exact", "icontains"],
            "sku": ["exact", "icontains"],
            "is_active": ["exact"],
        }




class ProductNode(DjangoObjectType):
    average_rating = graphene.Float()
    total_reviews = graphene.Int()

    class Meta:
        model = Product
        interfaces = (relay.Node,)
        filterset_class = ProductFilter  

    @classmethod
    def get_queryset(cls, queryset, info):
        user = info.context.user
        if not (user.is_authenticated and user.is_superuser):
            queryset = queryset.filter(is_active=True)
        return queryset

    def resolve_average_rating(self, info):
        return self.average_rating

    def resolve_total_reviews(self, info):
        return self.total_reviews


class ProductItemNode(DjangoObjectType):
    class Meta:
        model = ProductItem
        interfaces = (relay.Node,)
        filterset_class = ProductItemFilter

    @classmethod
    def get_queryset(cls, queryset, info):
        """
        Normal kullanıcılar is_active=False ProductItem'ları göremez.
        Admin kullanıcılar tüm ProductItem'ları görebilir.
        """
        user = info.context.user
        if not (user.is_authenticated and user.is_superuser):
            queryset = queryset.filter(is_active=True)
        return queryset

    def resolve_stock(self, info):
        """
        Stok bilgisi: Eğer ürün aktif değilse, sadece admin görebilir.
        (Burada get_queryset'te zaten is_active=False item'lar elenmiş durumda;
         ancak admin kendi sorgusunda is_active=False'u görebilir ve stok verisine erişebilir.)
        """
        user = info.context.user

        if not self.is_active and (not user.is_superuser):
            return None
        return self.stock

class VariationOptionFilter(django_filters.FilterSet):
    class Meta:
        model = VariationOption

        fields = {

            'name': ['exact', 'icontains'],
            'variation__name': ['exact', 'icontains']
        }

class VariationOptionNode(DjangoObjectType):
    class Meta:
        model = VariationOption
        interfaces = (relay.Node,)
        filterset_class = VariationOptionFilter  



class ProductItemInput(graphene.InputObjectType):

    id = graphene.ID(required=False)  # Güncelleme için
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)
    sku = graphene.String(required=True)
    variation_option_ids = graphene.List(graphene.ID, required=False)
    is_active = graphene.Boolean(required=False)


class CreateProduct(relay.ClientIDMutation):

    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        category_id = graphene.Int(required=True)
        items = graphene.List(ProductItemInput, required=True)
        is_active = graphene.Boolean(required=False)

    product = graphene.Field(ProductNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to create products.")
        if not user.is_superuser:
            raise Exception("Only admin users can create products.")

        name = input.get("name")
        description = input.get("description")
        category_id = input.get("category_id")
        items = input.get("items", [])
        is_active = input.get("is_active", True)

        if not items:
            raise Exception("At least one product item must be provided.")

        try:
            # Generate a unique slug
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            product = Product.objects.create(
                name=name,
                description=description,
                category_id=category_id,
                slug=slug,
                created_at=timezone.now(),
                is_active=is_active
            )
        except Exception as e:
            raise Exception(f"Error creating product: {str(e)}")

        for item in items:
            try:
                # It comes without an ID, meaning it will be newly created
                item_is_active = item.get("is_active", True)
                product_item = ProductItem.objects.create(
                    product=product,
                    name=item["name"],
                    price=item["price"],
                    stock=item["stock"],
                    sku=item["sku"],
                    is_active=item_is_active
                )

                if item.get("variation_option_ids"):
                    variation_options = VariationOption.objects.filter(id__in=item["variation_option_ids"])
                    product_item.variation_options.set(variation_options)
            except Exception as e:
                raise Exception(f"Error creating product item: {str(e)}")

        return CreateProduct(product=product)


class UpdateProduct(relay.ClientIDMutation):

    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        category_id = graphene.Int(required=False)
        items = graphene.List(ProductItemInput, required=False)
        is_active = graphene.Boolean(required=False)

    product = graphene.Field(ProductNode)

    @classmethod
    @login_required
    @admin_required
    def mutate_and_get_payload(cls, root, info, **input):
        product_global_id = input.get("id")
        product_pk = relay.Node.from_global_id(product_global_id)[1]  
        name = input.get("name")
        description = input.get("description")
        category_id = input.get("category_id")
        items = input.get("items", [])
        is_active = input.get("is_active")

        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            raise Exception("Product not found")

        if name:
            product.name = name
            product.slug = slugify(name)
        if description:
            product.description = description
        if category_id:
            product.category_id = category_id
        if is_active is not None:
            product.is_active = is_active

        product.save()

        if items:
            for item_data in items:
                item_id_global = item_data.get("id")

                if item_id_global:
                    item_pk = relay.Node.from_global_id(item_id_global)[1]
                    try:
                        product_item = ProductItem.objects.get(pk=item_pk, product=product)
                    except ProductItem.DoesNotExist:
                        raise Exception("ProductItem not found or does not belong to this product.")

                    product_item.name = item_data.get("name", product_item.name)
                    product_item.price = item_data.get("price", product_item.price)
                    product_item.stock = item_data.get("stock", product_item.stock)
                    product_item.sku = item_data.get("sku", product_item.sku)
                    if "is_active" in item_data:
                        product_item.is_active = item_data["is_active"]
                    product_item.save()

                    if "variation_option_ids" in item_data:
                        variation_ids = [
                            relay.Node.from_global_id(vid)[1] for vid in item_data["variation_option_ids"]
                        ]
                        variation_options = VariationOption.objects.filter(id__in=variation_ids)
                        product_item.variation_options.set(variation_options)

                else:

                    new_item_is_active = item_data.get("is_active", True)
                    new_product_item = ProductItem.objects.create(
                        product=product,
                        name=item_data["name"],
                        price=item_data["price"],
                        stock=item_data["stock"],
                        sku=item_data["sku"],
                        is_active=new_item_is_active
                    )
                    if item_data.get("variation_option_ids"):
                        variation_ids = [
                            relay.Node.from_global_id(vid)[1] for vid in item_data["variation_option_ids"]
                        ]
                        variation_options = VariationOption.objects.filter(id__in=variation_ids)
                        new_product_item.variation_options.set(variation_options)

        return UpdateProduct(product=product)




class Query(graphene.ObjectType):

    node = relay.Node.Field()


    all_products = DjangoFilterConnectionField(ProductNode)
    all_product_items = DjangoFilterConnectionField(ProductItemNode)
    all_variation_options = DjangoFilterConnectionField(VariationOptionNode)


    product = relay.Node.Field(ProductNode)
    product_item = relay.Node.Field(ProductItemNode)
    variation_option = relay.Node.Field(VariationOptionNode)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
