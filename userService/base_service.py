import json

import requests

from userService.errors import ResponseError, ValidationError


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
                                     json=introspection_query)
            if response.status_code == 200:
                pass
            else:
                raise ResponseError(f"{self.service_name}"
                                    f" Service is not answering")
        except requests.exceptions.RequestException:
            raise ResponseError(f"{self.service_name} Service is not answering"
                                )

    def _request(self, title: str, user_id):
        template = '''mutation{{createGoodsList(title:"{0}"){{id title}}}}'''
        query = template.format(title)
        response = requests.post(self.url,
                                 data={'query': query},
                                 headers={'AUTHORIZATION': user_id}
                                 )
        self._validate_errors(response)

    @staticmethod
    def _validate_errors(response):
        if 'errors' in str(response.content):
            cleaned_json = json.loads(
                response.content.decode('utf-8').replace("/", "")
            )['errors']
            raise ValidationError(cleaned_json[0]['message'])

    def _create_item(self, title: str, user_id):
        self._verify_connection()
        self._request(title=title, user_id=str(user_id))
