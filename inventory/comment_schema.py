import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Avg
from .models import Comment, Product

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ('id', 'user', 'product', 'content', 'rating', 'created_at')

class CreateComment(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)
        content = graphene.String(required=True)
        rating = graphene.Int(required=True)

    comment = graphene.Field(CommentType)

    def mutate(self, info, product_id, content, rating):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to add a comment.")

        if not 1 <= rating <= 5:
            raise GraphQLError("Rating must be between 1 and 5.")

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found.")

        # Check if user already commented on this product
        if Comment.objects.filter(user=user, product=product).exists():
            raise GraphQLError("You have already reviewed this product.")

        comment = Comment.objects.create(
            user=user,
            product=product,
            content=content,
            rating=rating
        )

        return CreateComment(comment=comment)

class UpdateComment(graphene.Mutation):
    class Arguments:
        comment_id = graphene.Int(required=True)
        content = graphene.String(required=False)
        rating = graphene.Int(required=False)

    comment = graphene.Field(CommentType)

    def mutate(self, info, comment_id, content=None, rating=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to update a comment.")

        try:
            comment = Comment.objects.get(pk=comment_id, user=user)
        except Comment.DoesNotExist:
            raise GraphQLError("Comment not found or you don't have permission to update it.")

        if rating is not None:
            if not 1 <= rating <= 5:
                raise GraphQLError("Rating must be between 1 and 5.")
            comment.rating = rating

        if content is not None:
            comment.content = content

        comment.save()
        return UpdateComment(comment=comment)

class DeleteComment(graphene.Mutation):
    class Arguments:
        comment_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, comment_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to delete a comment.")

        try:
            comment = Comment.objects.get(pk=comment_id, user=user)
            comment.delete()
            return DeleteComment(success=True)
        except Comment.DoesNotExist:
            raise GraphQLError("Comment not found or you don't have permission to delete it.")

class ProductRatingType(graphene.ObjectType):
    average_rating = graphene.Float()
    total_reviews = graphene.Int()
    rating_distribution = graphene.List(graphene.Int)

    def resolve_rating_distribution(self, info):
        """Returns list of count for each rating (1-5)"""
        distribution = []
        for i in range(1, 6):
            count = Comment.objects.filter(product_id=self.id, rating=i).count()
            distribution.append(count)
        return distribution

class Query(graphene.ObjectType):
    product_comments = graphene.List(
        CommentType,
        product_id=graphene.Int(required=True)
    )
    my_comments = graphene.List(CommentType)
    product_rating = graphene.Field(
        ProductRatingType,
        product_id=graphene.Int(required=True)
    )

    def resolve_product_comments(self, info, product_id):
        return Comment.objects.filter(product_id=product_id).order_by('-created_at')

    def resolve_my_comments(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to view your comments.")
        return Comment.objects.filter(user=user).order_by('-created_at')

    def resolve_product_rating(self, info, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            return ProductRatingType(
                id=product_id,
                average_rating=product.average_rating,
                total_reviews=product.total_reviews
            )
        except Product.DoesNotExist:
            raise GraphQLError("Product not found.")

class Mutation(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field() 