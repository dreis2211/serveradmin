# Django settings for Serveradmin project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'serveradmin',
        'USER': 'serveradmin',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'connect_timeout': 1,
            'client_encoding': 'UTF8',
            'options': '-c lock_timeout=10000',
        },
        # Wrap the requests into a database transaction
        'ATOMIC_REQUESTS': True,
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'SET-RANDOM-SECRET-KEY'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'serveradmin.api.middleware.ApiMiddleware',
    'serveradmin.hooks.middleware.HooksMiddleware',
)

ROOT_URLCONF = 'serveradmin.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'serveradmin.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'markup_deprecated',
    'serveradmin.common',
    'serveradmin.servershell',
    'serveradmin.apps',
    'serveradmin.dataset',
    'serveradmin.api',
    'serveradmin.docs',
    'serveradmin.iprange',
    'serveradmin.graphite',
    'serveradmin.resources',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

OBJECTS_PER_PAGE = 25

# Graphite URL is required to generate graphic URL's.  Normal graphs
# are requested from Graphite on the browser.  admin_djangourlauth module
# module is used to authenticate to Graphite.  Graphite secret is required
# to generate the tokens with this module.  Small graphs on the overview page
# are requested and stored by the Serveradmin from the Graphite. Graphs are
# stored by the job called "gensprites" under directory
# graphite/static/graph_sprite.  They are also merged into single images
# for every server to reduce the requests to the Serveradmin from the browser.
GRAPHITE_URL = 'https://graphite.innogames.de'
GRAPHITE_SECRET = 'f48bb9bcda4647f181c8255577c20313'
GRAPHITE_SPRITE_PATH = MEDIA_ROOT + '/graph_sprite'
GRAPHITE_SPRITE_URL = MEDIA_URL + 'graph_sprite'
GRAPHITE_SPRITE_WIDTH = 112
GRAPHITE_SPRITE_HEIGHT = 45
GRAPHITE_SPRITE_SPACING = 8
GRAPHITE_SPRITE_PARAMS = ('width=' + str(GRAPHITE_SPRITE_WIDTH) + '&' +
                          'height=' + str(GRAPHITE_SPRITE_HEIGHT) + '&' +
                          'graphOnly=true')

raise Exception('Set SECRET_KEY and DATABASE PASSWORD and remove this!')
