import os
import sys


def rel(*x):
    return os.path.join(os.path.dirname(__file__), *x)

sys.path.insert(0, rel('..', 'lib'))

GEOIP_PATH = os.path.join(rel('..', 'lib'), 'geoip')
GEOIP_DEBUG = True

GOOGLE_API_KEY = 'AIzaSyAe9JodBrnCM2Pc-2NdzieA27VCLYaERRE'

# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
# Hardcoded values can leak through source control. Consider loading
# the secret key from an environment variable or a file instead.
SECRET_KEY = 'jxi+z4+clfb=h4e1#@o_px270dprtqn1e+st6bb%kumglg-@0f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
    rel('templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'context.settings',
)

# Application definition

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.gis',
    'django.contrib.sites',
    'django.contrib.flatpages',

    'south',

    'content',
    'subscribers',
    'subscriptions',
    'precalculated',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar',)
INTERNAL_IPS = ('127.0.0.1',)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default'
    },
    'addresses': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'addresses'
    },
    'paths': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'paths'
    },
    'tickets': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tickets'
    },
}

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'


# not used for now
LIMIT_LATITUDES = (-125, -114)
LIMIT_LONGTITUDES = (32, 42)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'parkroulette2012',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'parkroulette.com',
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Pacific'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ENABLE_PRECALCULATED = True

# GEOCODING_PROVIDER = 'google'
GEOCODING_PROVIDER = 'bing'

STATIC_ROOT = rel('..', 'files')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    rel('static'),
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


try:
    from settings_local import *
except ImportError:
    pass
