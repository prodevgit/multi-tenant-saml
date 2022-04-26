from configparser import ConfigParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

config = ConfigParser()
config.read('../tenant_conf.ini')

DATABASE_USER = config.get('database', 'DATABASE_USER')
DATABASE_PASSWORD = config.get('database', 'DATABASE_PASSWORD')
DATABASE_HOST = config.get('database', 'DATABASE_HOST')
DATABASE_PORT = config.get('database', 'DATABASE_PORT')
DATABASE_NAME = config.get('database', 'DATABASE_NAME')


SECRET_KEY = 'lzac6+*w8y*!+q+0!e26ub3(go)(i8)x-2k5s3lj4!wh1mu=5w'

DEBUG = True

ALLOWED_HOSTS = ['*']

APP_URL = config.get('settings', 'APP_URL')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    'accounts',
    'management',
    'tenants'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'MultiTenantSAML.middleware.TenantMiddleware',
]

ROOT_URLCONF = 'MultiTenantSAML.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'MultiTenantSAML.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(thread)d %(filename)s %(funcName)s %(lineno)d: %(message)s',
            'datefmt': '%a, %d %b %Y %H:%M:%S %z',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': '/srv/applogs/tenant.log',
            'formatter': 'default',
        },
        "console": {"class": "logging.StreamHandler"},
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['mail_admins', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        "django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]},
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

AUTH_USER_MODEL = "accounts.User"

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ORIGIN_REGEX_WHITELIST = [
    r"^https://(?:.+\.)?prolancehub\.in$",
    r'^(http?://)?localhost:\d{4}',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': f"{DATABASE_NAME}",
        'USER': f"{DATABASE_USER}",
        'PASSWORD': f"{DATABASE_PASSWORD}",
        'HOST': f"{DATABASE_HOST}",
        'PORT': DATABASE_PORT,
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sql_mode': 'traditional',
            'charset': 'utf8mb4',
            'init_command': f'ALTER DATABASE {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci',
        },
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

IDP_ENTITY_ID = config.get('saml', 'IDP_ENTITY_ID')
IDP_SINGLE_SIGN_ON = config.get('saml', 'IDP_SINGLE_SIGN_ON')
IDP_SINGLE_LOGOUT = config.get('saml', 'IDP_SINGLE_LOGOUT')
SAML_CERTIFICATE = config.get('saml', 'SAML_CERTIFICATE')
SP_ENTITY_ID = config.get('saml', 'SP_ENTITY_ID')
ASSERTION_CONSUMER_SERVICE = config.get('saml', 'ASSERTION_CONSUMER_SERVICE')
SP_LOGOUT = config.get('saml', 'SP_LOGOUT')
SECURE_SAML = config.get('saml', 'SECURE_SAML')