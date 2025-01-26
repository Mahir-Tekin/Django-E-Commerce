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

class UpdateCategory(graphene.Mutation):
    print("lol")
    class Arguments:
        id = graphene.Int(required=True)  
        name = graphene.String(required=False)  
        parent_id = graphene.Int(required=False)  
        image_url = graphene.String(required=False)  
        slug = graphene.String(required=False)  
    category = graphene.Field(CategoryType)  

    def mutate(self, info, id, name=None, parent_id=None, image_url=None, slug=None):
        
        try:
            category = Category.objects.get(pk=id)
            print("lol")
        except Category.DoesNotExist:
            print("lol2")
            raise Exception("Category with the given ID does not exist.")

        if parent_id:
            try:
                parent = Category.objects.get(pk=parent_id)
                category.parent = parent
            except Category.DoesNotExist:
                raise Exception("Parent category with the given ID does not exist.")


        if name:
            category.name = name
        if image_url:
            category.image_url = image_url
        if slug:
            category.slug = slug

        category.save()

        return UpdateCategory(category=category)
    
    
class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)  # Silinecek kategorinin ID'si

    success = graphene.Boolean()  
    message = graphene.String()  

    def mutate(self, info, id):
        try:

            category = Category.objects.get(pk=id)
            category.delete()
            return DeleteCategory(success=True, message=f"Category with ID {id} deleted successfully.")
        except Category.DoesNotExist:

            return DeleteCategory(success=False, message=f"Category with ID {id} does not exist.")

class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()