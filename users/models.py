from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from django.contrib.auth.models import AbstractUser

from userService.errors import UnauthorizedError


class ExtendedUser(AbstractUser):
    # roles are: 1-user. 2-seller. 3-admin
    role = models.IntegerField(blank=False, default=1, validators=[
        MinValueValidator(1), MaxValueValidator(3)])
    address = models.CharField(max_length=256, null=True)
    firstname = models.CharField(max_length=256, null=True)
    lastname = models.CharField(max_length=256, null=True)
    image = models.CharField(max_length=5000, null=True, blank=True)

    def is_user(self):
        return self.role == 1

    def is_seller(self):
        return self.role == 2

    def is_admin(self):
        return self.role == 3

    def update_with_permissions(self, info, email, address,
                                firstname, lastname, image):
        """
        TODO write docs

        :param image:
        :param info:
        :param email:
        :param address:
        :param firstname:
        :param lastname:
        :return:
        """
        user: ExtendedUser = info.context.user
        if ((user.is_user() or
             user.is_seller()) and self == user) or\
                user.is_admin():
            if email is not None:
                self.email = email
            if address is not None:
                self.address = address
            if firstname is not None:
                self.firstname = firstname
            if lastname is not None:
                self.lastname = lastname
            if image is not None:
                self.image = image
            self.save()

        else:
            raise UnauthorizedError(
                "Not enough permissions to call this endpoint")

    def delete_with_permission(self, info):
        """
        TODO add docstring

        :param info:
        :return:
        """
        user: ExtendedUser = info.context.user
        if user.is_admin():
            self.delete()
        elif (user.is_seller() or user.is_user()) and self == user:
            self.delete()
        else:
            raise UnauthorizedError(
                "Not enough permissions to call this endpoint")
