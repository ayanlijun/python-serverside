from .base import *
from serverside.logging import get_logger
from serverside.aws import s3_client

MODE = DEV_MODE
LOGGER = get_logger(name="MAINSERVICE")


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dev",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": f"postgres",
        "PORT": "5432",
        "TEST": {
            "NAME": f"test",
        },
    },
}

S3_CLIENT = s3_client(
    endpoint_url="",
    aws_access_key_id="",
    aws_secret_access_key="",
    use_ssl=True
)
