import graphene
from decouple import config
from graphene_django import DjangoObjectType

from userService.base_service import BaseService
from users.models import ExtendedUser


class UserType(DjangoObjectType):
    class Meta:
        model = ExtendedUser


class GoodsListTransferType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    user = graphene.Field(UserType)

    def __init__(self, id=None, title=None, user=None, goods=None):
        self.id = id
        self.title = title
        self.user = user
        self.goods = goods


class ProductService(BaseService):

    url = config('PRODUCT_SERVICE_URL', default=False, cast=str)
    service_name = 'Product'

    def create_goods_list(self, title: str, user_id):
        self._create_item(title=title, user_id=user_id)

