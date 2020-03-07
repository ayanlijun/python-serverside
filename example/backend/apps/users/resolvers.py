import typing as ty
import requests
import uuid
from datetime import datetime, timedelta
from apps.users.models import User, Action, PermissionGroup
from django.conf import settings
from serverside.auth import validate_password, generate_hashed_password
from serverside.generators import Identicon
from serverside.graphql.ariadne import ObjectType, BaseResolver, auto_crud
from serverside.django.fields import S3FieldObject


class UserResolvers(BaseResolver):

    class Meta:
        model = User
        auto_crud = auto_crud(
            count="userCount", get_one="user", get_many="users",
            delete="deleteUser"
        )
        uid_gen = lambda: str(uuid.uuid4())

    user = ObjectType("User")

    @staticmethod
    @user.field("avatarUrl")
    async def get_avatar_url(obj, *args, **kwargs):
        return settings.S3_CLIENT(
            url="",
            bucket=obj.avatar.bucket,
            key=obj.avatar.key,
            https=True
        )

    @staticmethod
    @settings.QUERY.field("login")
    async def resolve_login(_, info, username: str, password: str):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return {"error": True, "message": "No user exists with this username.", "user": None, "token": None}
        if validate_password(password, user.password) is False:
            return {"error": True, "message": "Password was incorrect.", "user": None, "token": None}
        return {
            "error": False,
            "message": "Successful login.",
            "user": user,
            "token": settings.JWT_AUTH.encode_jwt(
                payload={"user_id": user.id},
                expiration=datetime.now() + timedelta(hours=1)
            )
        }

    @staticmethod
    @settings.MUTATION.field("createUser")
    async def resolve_create(_, info, input: ty.Dict):
        # TODO- Actually fill this out properly
        response = {"error": False, "message": "Create Successfull!", "node": None}
        try:
            id = str(uuid.uuid4())
            password = input.pop("password")
            avatar_bytes = Identicon(id).identicon
            key, presigned_url = settings.S3_CLIENT.generate_presigned_url(
                bucket="",
                key="",
                content_type="image/png",
                method="",
            )
            requests.put(
                presigned_url,
                data=avatar_bytes,
                headers={"Content-Type": "image/png"}
            )
            permission_group = PermissionGroup.objects.get(name="")
            inst = User.objects.create(**{
                **input,
                "id": id,
                "password": generate_hashed_password(password),
                "avatar": S3FieldObject(location="", bucket="", key=""),
                "permission_group": permission_group
            })
            inst.save()
            return {**response, "node": inst}
        except Exception as err:
            return {**response, "error": True, "message": f"Create Error: {err}"}

    @staticmethod
    @settings.MUTATION.field("updateUser")
    async def resolve_update(_, info, id: str, input: ty.Dict):
        response = {"error": False, "message": "Create Successfull!", "node": None}
        try:
            inst = User.objects.get(id=id)
            if "password" in input:
                password = input.pop("password")
                inst.password = generate_hashed_password(password)
            for k, v in input.items():
                setattr(inst, k, v)
            inst.save()
            return {**response, "node": inst}
        except User.DoesNotExist:
            return {**response, "error": True, "message": f"The object with id {id} could not be found."}
        except Exception as err:
            return {**response, "error": True, "message": f"Create Error: {err}"}


class ActionResolvers(BaseResolver):

    class Meta:
        model = Action
        auto_crud = auto_crud(
            count="actionCount", get_one="action", get_many="actions",
            create="createAction", update="updateAction", delete="deleteAction"
        )
        uid_gen = lambda: str(uuid.uuid4())


class PermissionGroupResolvers(BaseResolver):

    class Meta:
        model = PermissionGroup
        auto_crud = auto_crud(
            count="permissionGroupCount", get_one="permissionGroup", get_many="permissionGroups",
            create="createPermissionGroup", update="updatePermissionGroup", delete="deletePermissionGroup"
        )
        uid_gen = lambda: str(uuid.uuid4())


def export_resolvers() -> ty.List:
    return [
        UserResolvers,
        ActionResolvers,
        PermissionGroupResolvers
    ]
