import graphene
from graphene_django.types import DjangoObjectType
from .models import Variation, VariationOption

class VariationType(DjangoObjectType):
    class Meta:
        model = Variation
        fields = ("id", "name", "options")  

    options = graphene.List(lambda: VariationOptionType)  

    def resolve_options(self, info):
        return self.options.all()

class VariationOptionType(DjangoObjectType):
    class Meta:
        model = VariationOption
        fields = ("id", "name", "variation")

class CreateVariation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True) 
        options = graphene.List(graphene.String, required=True) 

    variation = graphene.Field(VariationType)

    def mutate(self, info, name, options):
        
        variation = Variation.objects.create(name=name)

        for option_name in options:
            VariationOption.objects.create(variation=variation, name=option_name)

        return CreateVariation(variation=variation)


class OptionInput(graphene.InputObjectType):
    id = graphene.Int()  
    name = graphene.String(required=True)  

class UpdateVariation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)  
        name = graphene.String(required=False)  
        options = graphene.List(OptionInput, required=True) 

    variation = graphene.Field(VariationType)

    def mutate(self, info, id, name=None, options=None):
        try:
            
            variation = Variation.objects.get(pk=id)
 
            if name:
                variation.name = name
        
            existing_options = VariationOption.objects.filter(variation=variation)
            existing_ids = [opt.id for opt in existing_options]
     
            for option_input in options:
                if option_input.id:  
                    if option_input.id in existing_ids:
                        existing_option = existing_options.get(pk=option_input.id)
                        existing_option.name = option_input.name
                        existing_option.save()
                else:  
                    VariationOption.objects.create(variation=variation, name=option_input.name)

            sent_ids = [opt.id for opt in options if opt.id]
            for option in existing_options:
                if option.id not in sent_ids:
                    option.delete()

            variation.save()
            return UpdateVariation(variation=variation)
        except Variation.DoesNotExist:
            raise Exception("Variation not found")

class DeleteVariation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)  

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            variation = Variation.objects.get(pk=id)
            variation.delete()
            return DeleteVariation(success=True)
        except Variation.DoesNotExist:
            raise Exception("Variation not found")

class Query(graphene.ObjectType):
    all_variations = graphene.List(VariationType)
    variation_by_id = graphene.Field(VariationType, id=graphene.Int(required=True))

    def resolve_all_variations(self, info):
        return Variation.objects.all()

    def resolve_variation_by_id(self, info, id):
        try:
            return Variation.objects.get(pk=id)
        except Variation.DoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    create_variation = CreateVariation.Field()
    update_variation = UpdateVariation.Field()
    delete_variation = DeleteVariation.Field()
