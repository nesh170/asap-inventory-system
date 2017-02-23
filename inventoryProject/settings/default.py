"""
Django settings for inventoryProject project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

try:
    with open(os.path.join(__location__, 'secret_key.txt')) as f:
        SECRET_KEY = f.read().strip()
except IOError as e:
    SECRET_KEY = os.environ['SECRET_KEY']


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'items.apps.ItemsConfig',
    'rest_framework',
    'inventory_logger.apps.InventoryLoggerConfig',
    'inventory_user.apps.InventoryUserConfig',
    'inventory_disbursements.apps.InventoryDisbursementsConfig',
    'items.fixtures',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'rest_framework.authtoken',
    'corsheaders',
    'inventory_shopping_cart.apps.InventoryShoppingCartConfig',
    'inventory_shopping_cart_request.apps.InventoryShoppingCartRequestConfig',
    'inventory_transaction_logger.apps.InventoryTransactionLoggerConfig'
]

# SOCIAL_AUTH_DUKE_AUTH_EXTRA_ARGUMENTS = {'scope': 'basic identity:netid:read'}
SOCIAL_AUTH_DUKE_KEY = 'asap-inventory-system'
SOCIAL_AUTH_DUKE_SECRET = '4VBvMIAw*KA5oL7EnoG8aLYY=*Tnrmb9o$$+Gqyxe$LYf@skQL'
SOCIAL_AUTH_DUKE_SCOPE = ['basic', 'identity:netid:read']

DRFSO2_PROPRIETARY_BACKEND_NAME = 'duke'



AUTHENTICATION_BACKENDS = (
    'inventoryProject.dukeAuth.DukeOAuth2',
    'django.contrib.auth.backends.ModelBackend'
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_WHITELIST = (
    'asap-production.colab.duke.edu',
    'asap-test.colab.duke.edu',
    'kipcoonley.com',
    'colab-sbx-86.oit.duke.edu',
    'localhost:3000'
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'},
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600
}

ROOT_URLCONF = 'inventoryProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventoryProject.wsgi.application'




# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
try:
    with open(os.path.join(__location__, 'db_password.txt')) as f:
        DB_PASSWORD = f.read().strip()
    with open(os.path.join(__location__, 'db_hostname.txt')) as f:
        DB_HOSTNAME = f.read().strip()
except IOError as e:
    DB_PASSWORD = os.environ['DB_PASSWORD']
    DB_HOSTNAME = os.environ['DB_HOSTNAME']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'asap_db',
        'USER': 'postgres',
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOSTNAME,
        'PORT': '5432',
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

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30,
    'SEARCH_PARAM': "search",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'