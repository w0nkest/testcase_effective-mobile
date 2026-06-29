from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Create your models here.
class UserProfile(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserProfileManager()

    def __str__(self):
        return f'{self.name} {self.surname}'


class Roles(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class UserRole(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)


class Resource(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class Access(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

    can_read = models.BooleanField(default=False)
    can_read_all = models.BooleanField(default=False)

    can_create = models.BooleanField(default=False)

    can_update = models.BooleanField(default=False)
    can_update_all = models.BooleanField(default=False)

    can_delete = models.BooleanField(default=False)
    can_delete_all = models.BooleanField(default=False)


# class UserProfile(models.Model):
#     name = models.CharField(max_length=255)
#     surname = models.CharField(max_length=255)
#     email = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)