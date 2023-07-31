import graphene
from django.db.models import Q

from userService.authorization import grant_authorization
from userService.product_service import ProductService, UserType
from users.models import ExtendedUser


product_service = ProductService()


class Query(graphene.ObjectType):
    users = graphene.List(UserType,
                          search=graphene.String(),
                          sub=graphene.String(),
                          searched_id=graphene.Int())

    def resolve_users(self,
                      info,
                      searched_id=None,
                      search=None,
                      sub=None,
                      **kwargs):
        """
        TODO add docs

        :param sub:
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
        if sub:
            return [ExtendedUser.objects.filter(sub=sub).first()]
        return ExtendedUser.objects.all()


class CreateUser(graphene.Mutation):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    role = graphene.Int()
    address = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    image = graphene.String()
    sub = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String()
        role = graphene.Int(required=True)
        address = graphene.String()
        firstname = graphene.String()
        lastname = graphene.String()
        image = graphene.String()
        sub = graphene.String()

#    @grant_authorization
    def mutate(self,
               info,
               username,
               email,
               role,
               image=None,
               address=None,
               firstname=None,
               lastname=None,
               sub=None):
        """
        TODO add docs

        :param sub:
        :param info:
        :param username:
        :param email:
        :param role:
        :param image:
        :param address:
        :param firstname:
        :param lastname:
        :return:
        """
        validate_role(role)
        # TODO users can not create admins
        user = ExtendedUser(
            username=username,
            email=email,
            role=role,
            address=address,
            lastname=lastname,
            firstname=firstname,
            image=image,
            # TODO extract sub from token if user or seller
            sub=sub
        )
        user.save()
        product_service.create_goods_list_when_signup(info=info,
                                                      title="cart",
                                                      sub=sub)
        product_service.create_goods_list_when_signup(info=info,
                                                      title="liked",
                                                      sub=sub)
        if user.is_seller():
            product_service.create_goods_list_when_signup(
                info=info,
                title="goods_to_sell",
                sub=sub)
        return CreateUser(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            address=user.address,
            lastname=user.lastname,
            firstname=user.firstname,
            image=user.image,
            sub=user.sub
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

    @grant_authorization
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

    @grant_authorization
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
