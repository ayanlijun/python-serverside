import os
from serverside import State
from serverside.auth import JWTAuth
from serverside.graphql.ariadne import QueryType, MutationType


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


JWT_AUTH = JWTAuth(
    secret_key="z+rofb5nmzs@hhdgz6f#b%p71y8krs$an+%p8k&&643!==&f2q",
    encode_algorithm="HS512",
    decode_algorithms=["HS512"]
)

DEV_MODE = "dev"
STAGE_MODE = "stage"
PROD_MODE = "prod"

USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = "en-us"
TIME_ZONE = 'UTC'

INSTALLED_APPS = [
    "apps.users"
]

MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",
]

SECRET_KEY = "<secret_key>"
ROOT_URLCONF = "config.urls"

STATIC_ROOT = f"/srv/static/"
STATIC_URL = "/static/"

STATE = State()
QUERY = QueryType()
MUTATION = MutationType()


#########################################
#  Translation
#########################################

LANGUAGES = (
    ('en-us', 'English'),
)
LOCALE_PATHS = ("/srv/locale",)
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.i18n"
]


#########################################
#  Templates
#########################################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["srv/static"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
