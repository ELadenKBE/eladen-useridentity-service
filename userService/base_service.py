import json

import requests
from graphql import GraphQLResolveInfo

from userService.errors import ResponseError, ValidationError, \
    UnauthorizedError


class BaseService:

    url = None
    service_name = None

    def _verify_connection(self):
        try:
            introspection_query = {
                "query": """
                            query {
                                __schema {
                                    queryType {
                                        name
                                    }
                                }
                            }
                        """
            }
            response = requests.post(self.url,
                                     data=introspection_query)
            if response.status_code == 200:
                pass
            else:
                raise ResponseError(f"{self.service_name}"
                                    f" Service is not answering")
        except requests.exceptions.RequestException:
            raise ResponseError(f"{self.service_name} Service is not answering"
                                )

    def _request(self, title: str, sub):
        """

        :param title:
        :param sub: authorisation token
        :return:
        """
        template = '''mutation{{createGoodsList(title:"{0}"){{id title}}}}'''
        query = template.format(title)
        response = requests.post(self.url,
                                 data={'query': query},
                                 headers={'AUTHORIZATION': sub}
                                 )
        self._validate_errors(response)

    @staticmethod
    def _validate_errors(response):
        if 'errors' in str(response.content):
            cleaned_json = json.loads(
                response.content.decode('utf-8').replace("/", "")
            )['errors']
            raise ValidationError(cleaned_json[0]['message'])

    def _create_item(self, title: str, sub: str):
        self._verify_connection()
        self._request(title=title, sub=sub)

    @staticmethod
    def _get_auth_header(info: GraphQLResolveInfo):
        try:
            auth_header: str = info.context.headers['AUTHORIZATION']
        except KeyError as key_error:
            raise UnauthorizedError('authorization error: AUTHORIZATION header'
                                    ' is not specified')
        except ResponseError as response_error:
            raise UnauthorizedError('authorization error: ',
                                    response_error.args[0])
        return auth_header
