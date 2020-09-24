"""
Django settings for chat project.
"""

import os
import requests

try:
    from django_jenkins.tasks import run_pylint


    class Lint:
        """
        Monkey patch to fix
        TypeError: __init__() got an unexpected keyword argument 'exit'.
        """
        class Run(run_pylint.lint.Run):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, do_exit=kwargs.pop("exit"), **kwargs)


    run_pylint.lint = Lint
except ImportError:
    run_pylint = None

SITE_ENV_PREFIX = 'CHAT'


def get_env_var(name, default=''):
    """ Get all sensitive data from google vm custom metadata. """
    try:
        name = '_'.join([SITE_ENV_PREFIX, name])
        res = os.environ.get(name)
        if res:
            # Check env variable (Jenkins build).
            return res
        else:
            res = requests.get(
                'http://metadata.google.internal/computeMetadata/'
                'v1/instance/attributes/{}'.format(name),
                headers={'Metadata-Flavor': 'Google'}
            )
            if res.status_code == 200:
                return res.text
    except requests.exceptions.ConnectionError:
        return default
    return default


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var(
    'SECRET_KEY',
    'q-=(1t*%^5*c98%&_cj9vr26(3_(3@f^bj&bw)atj(zn_g)r0@'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(get_env_var('DEBUG', 'True'))

INTERNAL_IPS = (
    '127.0.0.1',
)

ADMINS = [
    ('Mike', 'mriynuk@gmail.com')
]

ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    'social_django',
    'widget_tweaks',
    'chatterbot.ext.django_chatterbot',

    'core',
]

if DEBUG:
    from debug_toolbar.settings import PANELS_DEFAULTS

    INSTALLED_APPS += ['debug_toolbar', 'django_jenkins', 'debug_toolbar_line_profiler']
    DEBUG_TOOLBAR_PANELS = PANELS_DEFAULTS + [
        'ddt_request_history.panels.request_history.RequestHistoryPanel',
        'debug_toolbar_line_profiler.panel.ProfilingPanel',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social_django.middleware.SocialAuthExceptionMiddleware',

    'core.middleware.active_user_middleware',
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'chat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',

                'core.context_processors.unread_threads',
            ],
        },
    },
]

WSGI_APPLICATION = 'chat.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_var('DB_NAME', 'chat'),
        'USER': get_env_var('DB_USER', 'chat_admin'),
        'PASSWORD': get_env_var('DB_PASSWORD', 'chat_pass_!_12'),
        'HOST': get_env_var('DB_HOST', '127.0.0.1'),
        'PORT': '',
    }
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# CELERY STUFF
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 2 * 60  # 2 minutes

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Security
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_PRELOAD = True

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://localhost:6379/1'],
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('uk', 'Ukrainian'),
    ('it', 'Italian'),
    ('fr', 'French'),
    ('ru', 'Russian'),
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = 'core:login'

LOGOUT_URL = 'core:logout'

LOGIN_REDIRECT_URL = 'core:user_list'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'core:user_list'
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = 'core:user_list'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False
SOCIAL_AUTH_FACEBOOK_KEY = get_env_var('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = get_env_var('SOCIAL_AUTH_FACEBOOK_SECRET')

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 2525
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
MAILGUN_SERVER_NAME = 'chat.mkeda.me'
EMAIL_SUBJECT_PREFIX = '[Chat]'
SERVER_EMAIL = 'admin@chat.mkeda.me'

USE_X_FORWARDED_HOST = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = '/home/voron/sites/cdn/chat'

STATIC_URL = 'https://storage.googleapis.com/cdn.mkeda.me/chat/'
if DEBUG:
    STATIC_URL = '/static/'

STATICFILES_DIRS = (
    ("", os.path.join(BASE_DIR, "static")),
)

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                 'django_jenkins.tasks.run_pep8',
                 'django_jenkins.tasks.run_pyflakes',)

PROJECT_APPS = ['core', 'chat']

PYLINT_LOAD_PLUGIN = ['pylint_django']

GOOGLE_MAP_API_KEY = get_env_var('GOOGLE_MAP_API_KEY')

GEOIP_PATH = 'geo/'

ASGI_APPLICATION = "core.routing.chat"
CHATTERBOT = {
    'name': 'Chat Bot',
    'logic_adapters': [
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.1
        },
        {
            'import_path': 'chatterbot.logic.UnitConversion',
        },
        {
            'import_path': 'chatterbot.logic.MathematicalEvaluation',
        },
    ],
    'trainer': 'chatterbot.trainers.ChatterBotCorpusTrainer',
    'storage_adapter': 'chatterbot.storage.DjangoStorageAdapter',
    'training_data': [
        "chatterbot.corpus.english",
        "chatterbot.corpus.spanish",
        "chatterbot.corpus.italian",
        "chatterbot.corpus.french",
        "chatterbot.corpus.russian"
    ]
}
