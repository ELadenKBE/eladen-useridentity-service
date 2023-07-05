from django.contrib.auth import get_user_model

import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType

from userService.permissions import permission, Admin, All, Seller, User, Anon
from users.models import ExtendedUser


class UserType(DjangoObjectType):
    class Meta:
        model = ExtendedUser


class Query(graphene.ObjectType):
    users = graphene.List(UserType,
                          search=graphene.String(),
                          searched_id=graphene.Int())

    def resolve_users(self, info, searched_id=None, search=None, **kwargs):
        """
        TODO add docs

        :param info:
        :param searched_id:
        :param search:
        :param kwargs:
        :return:
        """
        if search:
            search_filter = (Q(username__icontains=search))
            return [ExtendedUser.objects.filter(search_filter).first()]
        if searched_id:
            return [ExtendedUser.objects.filter(id=searched_id).first()]
        return ExtendedUser.objects.all()


class CreateUser(graphene.Mutation):
    id = graphene.Int()
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    role = graphene.Int(required=True)
    address = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    image = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        role = graphene.Int(required=True)
        address = graphene.String()
        firstname = graphene.String()
        lastname = graphene.String()
        image = graphene.String()

#    @permission(roles=[Admin, Anon])
    def mutate(self,
               info,
               username,
               password,
               email,
               role,
               image=None,
               address=None,
               firstname=None,
               lastname=None):
        """
        TODO add docs

        :param info:
        :param username:
        :param password:
        :param email:
        :param role:
        :param image:
        :param address:
        :param firstname:
        :param lastname:
        :return:
        """
        validate_role(role)
        user = ExtendedUser(
            username=username,
            email=email,
            role=role,
            address=address,
            lastname=lastname,
            firstname=firstname,
            image=image
        )
        user.set_password(password)
        user.save()
        if user.is_user():
            # TODO add liked and cart
            # cart_list = GoodsList(title="cart", user=user)
            # cart_list.save()
            # liked = GoodsList(title="liked", user=user)
            # liked.save()
            pass
        if user.is_seller():
            # TODO add goods_to_sell
            # goods_to_sell = GoodsList(title="goods_to_sell", user=user)
            # goods_to_sell.save()
            pass
        return CreateUser(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            address=user.address,
            lastname=user.lastname,
            firstname=user.firstname,
            image=user.image
        )


class UpdateUser(graphene.Mutation):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    role = graphene.Int()
    address = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    image = graphene.String()

    class Arguments:
        user_id = graphene.Int(required=True)
        email = graphene.String()
        address = graphene.String()
        firstname = graphene.String()
        lastname = graphene.String()
        image = graphene.String()

#    @permission(roles=[Admin, Seller, User])
    def mutate(self,
               info,
               user_id,
               email=None,
               image=None,
               address=None,
               firstname=None,
               lastname=None):
        """
        TODO add docs

        :param info:
        :param user_id:
        :param email:
        :param image:
        :param address:
        :param firstname:
        :param lastname:
        :return:
        """
        user: ExtendedUser = ExtendedUser.objects.filter(id=user_id).first()
        user.update_with_permissions(info,
                                     email,
                                     address,
                                     firstname,
                                     lastname,
                                     image)
        return UpdateUser(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            address=user.address,
            firstname=user.firstname,
            lastname=user.lastname,
            image=user.image
        )


class DeleteUser(graphene.Mutation):
    id = graphene.Int(required=True)

    class Arguments:
        user_id = graphene.Int(required=True)

 #   @permission(roles=[Admin, Seller, User])
    def mutate(self, info, user_id):
        """
        TODO add docs

        :param info:
        :param user_id:
        :return:
        """
        user: ExtendedUser = ExtendedUser.objects.filter(id=user_id).first()
        user.delete_with_permission(info)
        return DeleteUser(
            id=user_id
        )


def validate_role(role):
    """
    TODO add docs

    :param role:
    :return:
    """
    if role < 1 or role > 3:
        raise ValueError("role is not defined")


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
