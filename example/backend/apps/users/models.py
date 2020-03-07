from __future__ import annotations
from django.db import models
from serverside.django.fields import S3Field
from django.conf import settings


class Action(models.Model):

    class Meta:
        ordering = ("-updated",)
        db_table = "users__actions"

    id = models.CharField(primary_key=True, max_length=64)
    action = models.CharField(max_length=255, unique=True, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class PermissionGroup(models.Model):

    class Meta:
        ordering = ("-updated",)
        db_table = "users__permissiongroups"

    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class User(models.Model):

    class Meta:
        ordering = ("-updated",)
        db_table = "users__users"

    id = models.CharField(primary_key=True, max_length=64)
    username = models.CharField(max_length=32, unique=True, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    avatar = S3Field(null=False)
    permission_group = models.ForeignKey(PermissionGroup, related_name="permissiongroup_users", on_delete=models.PROTECT)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def authenticate(token: str) -> User:
        authenticated, error_message, decoded_jwt = settings.JWT_AUTH.authenticate_jwt(token)
        if authenticated is True:
            user_id = decoded_jwt.get("user_id")
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise Exception("<User> could not be found.")
            except Exception as err:
                raise Exception(f"Authentication Failed: {err}")
        else:
            raise Exception(f"Authentication Failed: {error_message}")
