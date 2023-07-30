"""Product Service is used to create service lists when a user created.
"""
import urllib.parse

import graphene
from decouple import config
from graphene_django import DjangoObjectType
from graphql import GraphQLResolveInfo

from userService.base_service import BaseService
from users.models import ExtendedUser
import re


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
    # url = config('PRODUCT_SERVICE_URL',
    #              default="http://product-service:8082/graphql/",
    #              cast=str)
    url = "http://product-service:8082/graphql/"
    service_name = 'Product'

    def create_goods_list_when_signup(self,
                                      info: GraphQLResolveInfo,
                                      title: str):
        sub_auth = self._get_sub_when_signup(info)
        return self._create_item(title=title, sub="sub "+sub_auth)

    @staticmethod
    def _get_sub_when_signup(info: GraphQLResolveInfo):
        cleaned = info.context.body.decode('utf-8') \
            .replace('\\n', ' ') \
            .replace('\\t', ' ')
        cleaned = urllib.parse.unquote(cleaned).replace('+', ' ')
        # The modified regular expression pattern r'sub:\s*"([^"]*)"' will
        # match occurrences of "sub:" followed by optional whitespace (\s*),
        # double quotes ("), and then any characters that are not double
        # quotes ([^"]*).
        sub = re.search(r'sub:\s*"([^"]*)"', cleaned).group(1)
        return sub
