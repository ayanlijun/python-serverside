import os
import sys
import uuid
import django
from serverside.auth import generate_hashed_password
from serverside.django.fields import S3FieldObject
from serverside.generators import Identicon

sys.path.append('/modules')
this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.conf import settings
from apps.users.models import User, PermissionGroup


usernames = [
    "user_1",
    "user_2"
]

try:
    pm = PermissionGroup.objects.get(id="30138e59-4811-46eb-999e-1aec004d8bee")
except PermissionGroup.DoesNotExist:
    pm = PermissionGroup(
        id="30138e59-4811-46eb-999e-1aec004d8bee",
        name="default"
    )
    pm.save()


for username in usernames:
    try:
        user_inst = User.objects.get(username=username)
    except User.DoesNotExist:
        identicon = Identicon(username)
        user_inst = User.objects.create(
            id=str(uuid.uuid4()),
            username=username,
            password=generate_hashed_password("123"),
            name=username.title(),
            permission_group=pm,
            avatar=S3FieldObject(location="location", bucket="bucket", key="key")
        )
        user_inst.save()
