from django.contrib.auth.models import AnonymousUser

from userService.errors import UnauthorizedError, ResponseError
from users.models import ExtendedUser


def grant_authorization(func):
    """This decorator extracts id of user from AUTHORIZATION header
    and requests a user service to get a user information"""
    def wrapper(*arg, **kwargs):
        info = arg[1]
        try:
            auth_header: str = info.context.headers['AUTHORIZATION']
            user_sub = auth_header.split(' ')[1]
            user = ExtendedUser.objects.filter(sub=user_sub).first()
            if user is None:
                info.context.user = AnonymousUser()
            else:
                info.context.user = user
        except KeyError as key_error:
            raise UnauthorizedError('authorization error: AUTHORIZATION header'
                                    ' is not specified')
        except ResponseError as response_error:
            raise UnauthorizedError('authorization error: ',
                                    response_error.args[0])
        except Exception as error:
            # TODO specify exceptions at testing
            raise UnauthorizedError('authorization error: ', error)
        return func(*arg, **kwargs)
    return wrapper
