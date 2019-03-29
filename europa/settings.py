"""
Django settings for europa project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import europa
import sentry_sdk
from environment import env_var, read_env
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6d#dcrvly@mj0u5nyis&4h0+fzysma86a&fye%#$_co5bd*d$*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '0.0.0.0',
    '127.0.0.1',
    'europa',
    '.bink-dev.com',
    '.bink-sandbox.com',
    '.bink-staging.com',
    '.bink.com',
]


# Application definition

INSTALLED_APPS = [
    'raven.contrib.django.raven_compat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ddtrace.contrib.django',
    'config_service',
    'rest_framework',
    'nested_admin',
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config_service.request_exposer.ExposeRequestMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'


ROOT_URLCONF = 'europa.urls'

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

WSGI_APPLICATION = 'europa.wsgi.application'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = env_var('STATIC_URL', '/static/')

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

default = {
    'ENGINE': env_var('DB_ENGINE', 'django.db.backends.postgresql'),
    'NAME': env_var('DB_NAME', 'europa'),
    'USER': env_var('DB_USER', 'europa'),
    'PASSWORD': env_var('DB_PASSWORD', 'enrgn3478ty'),
    'HOST': env_var('DB_HOST', 'localhost'),
    'PORT': env_var('DB_PORT', '5432'),
}

test = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}


DATABASES = {
    'default': test if env_var('TESTING') else default
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'config_service.CustomUser'

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

NO_AZURE_STORAGE = env_var('NO_AZURE_STORAGE')

if not NO_AZURE_STORAGE:
    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
    AZURE_ACCOUNT_NAME = env_var('AZURE_ACCOUNT_NAME')
    AZURE_ACCOUNT_KEY = env_var('AZURE_ACCOUNT_KEY')
    AZURE_CONTAINER = env_var('AZURE_CONTAINER')
    AZURE_CUSTOM_DOMAIN = env_var('AZURE_CUSTOM_DOMAIN')


SENTRY_DSN = env_var('SENTRY_DSN', None)
if SENTRY_DSN:
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': europa.__version__,
    }

# HashiCorp Vault
VAULT_URL = env_var('VAULT_URL')
VAULT_TOKEN = env_var('VAULT_TOKEN')

ENVIRONMENT_ID = env_var('ENVIRONMENT_ID', 'dev').lower()
SENTRY_DSN = env_var('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT_ID,
        integrations=[
            DjangoIntegration()
        ]
    )

DATADOG_TRACE = {
    'DEFAULT_SERVICE': 'europa',
    'TAGS': {'env': env_var('DATADOG_APM_ENV')},
    'AGENT_HOSTNAME': env_var('DATADOG_APM_HOST', 'datadog-agent-trace.datadog'),
    'ENABLED': env_var('DATADOG_APM_ENABLED', False)
}
