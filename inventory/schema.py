import graphene
from graphene_django.types import DjangoObjectType
from .models import Category


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'image_url', 'slug', 'subcategories')


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType)  
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))  

    def resolve_categories(self, info):
        return Category.objects.all()

    def resolve_category(self, info, id):
        try:
            return Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return None


class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        parent_id = graphene.Int(required=False)
        image_url = graphene.String(required=False)
        slug = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    def mutate(self, info, name, slug, parent_id=None, image_url=None):
        parent = Category.objects.get(pk=parent_id) if parent_id else None
        category = Category.objects.create(name=name, slug=slug, parent=parent, image_url=image_url)
        return CreateCategory(category=category)

class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()