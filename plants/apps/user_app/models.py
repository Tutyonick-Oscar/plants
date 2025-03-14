from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from plants.apps.core.models import BaseModel, CustomBaseManager
from plants.apps.core.validators import special_characters_check, str_checker


class CustomUserManager(BaseUserManager, CustomBaseManager):

    def create_user(self, email, password, username, **kwargs):
        if not email:
            raise ValueError("The email is required !")
        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, username, **kwargs):
        user = self.create_user(email, password, username, **kwargs)
        user.is_admin = True
        user.save()
        return user


class CustomUser(BaseModel, AbstractBaseUser, PermissionsMixin):

    class UserRolesChoices(models.TextChoices):
        MARCHANT = "M", _("Marchant")
        FARMER = "F", _("Farmer")
        SIMPLE_USER = "S", _("Simple_user")

    created_by = None
    username = models.CharField(max_length=50, validators=[str_checker])
    email = models.EmailField(unique=True, max_length=200, blank=False)
    password = models.CharField(
        ("password"),
        max_length=128,
        validators=[
            MaxLengthValidator(8),
            MinLengthValidator(6),
            special_characters_check,
        ],
    )
    role = models.CharField(
        max_length=1,
        choices=UserRolesChoices.choices,
        default=UserRolesChoices.SIMPLE_USER,
    )
    user_access_unit = models.DecimalField(
        max_digits=16, decimal_places=4, default=0.00
    )

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password", "username"]

    def __str__(self) -> str:
        return self.username

    objects = CustomUserManager()

    def has_perms(self, perms, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(deleted_at=None),
                name="unique_undeleted_user",
            )
        ]
        indexes = [
            models.Index(
                fields=("deleted_at",),
                name="indexing_undeleted_users",
                condition=models.Q(deleted_at=None),
            )
        ]
