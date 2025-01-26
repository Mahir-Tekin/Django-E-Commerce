import graphene
import inventory.category_schema
import inventory.variation_schema  
import inventory.product_schema
import users.authorization_schema


class Query(users.authorization_schema.Query, inventory.category_schema.Query, inventory.product_schema.Query, inventory.variation_schema.Query, graphene.ObjectType):
    pass

class Mutation(users.authorization_schema.Mutation, inventory.category_schema.Mutation,inventory.variation_schema.Mutation, inventory.product_schema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)