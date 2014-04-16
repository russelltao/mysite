"""
Django settings for myblog project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os import path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ROOT_PATH = path.abspath(path.join(path.dirname('settings.py'), path.pardir))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zs$3j9ydzu(zf)sflvseitey+=tmauh15*ekq1gta=!^_d%a60'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition
TEMPLATE_DIRS=[  
        os.path.join(BASE_DIR,'myblog/blog/templates'),  
        ]  

DIRECTORY_URLS = (
    'http://ping.blogs.yandex.ru/RPC2',
    'http://rpc.technorati.com/rpc/ping',
)
# Application definition  
  
INSTALLED_APPS = (  
    'django.contrib.admin',  
    'django.contrib.auth',  
    'django.contrib.contenttypes',  
    'django.contrib.sessions',  
    'django.contrib.messages',  
    'django.contrib.staticfiles', 
    'django.contrib.sites',   
    'bootstrap3',
    'myblog.blog',  
    'duoshuo',
    'rstify',
    'django_xmlrpc',
    'userena', 
    'guardian',
    'easy_thumbnails',
    'accounts',
)  

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pingback.middleware.PingbackMiddleware',
    'myblog.blog.middleware.OnlineMiddleware',
    'userena.middleware.UserenaLocaleMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
)

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

USERENA_DISABLE_PROFILE_LIST = True

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'iamtaohui@gmail.com'
EMAIL_HOST_PASSWORD = 'BatMan20123'

ANONYMOUS_USER_ID = -1

AUTH_PROFILE_MODULE = 'accounts.MyProfile'

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'



ROOT_URLCONF = 'myblog.urls'

WSGI_APPLICATION = 'myblog.wsgi.application'

LOG_FILE = '/mnt/webLogs/myblog.log'
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'blog', 
        'USER': 'root', # Not used with sqlite3.
        'PASSWORD': 'iamtaohui', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(module)s : %(message)s'
        },
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] %(module)s : %(message)s'
        }
    },

    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': LOG_FILE,
            'mode': 'a',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false']
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 60,
        'options': {
            'MAX_ENTRIES': 1024,
        }
    },
    'memcache': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'unix:/mnt/memcached.sock',
        'TIMEOUT': 60,
        'options': {
            'MAX_ENTRIES': 1024,
        }
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-CN'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# https://docs.djangoproject.com/en/1.6/howto/static-files/
# Additional locations of static files  
HERE = os.path.dirname(__file__)  
STATICFILES_DIRS = (  
    # Put strings here, like "/home/html/static" or "C:/www/django/static".  
    # Always use forward slashes, even on Windows.  
    # Don't forget to use absolute paths, not relative paths.  
    HERE+STATIC_URL,  
)  

PAGE_NUM = 10
RECENTLY_NUM = 15
HOT_NUM = 15
ONE_DAY = 24*60*60
FIF_MIN = 15 * 60
FIVE_MIN = 5 * 60

SITE_ID = 1

DUOSHUO_SECRET = 'bfd5ce8cc34ab82ad96ae6ade39f81a8'
DUOSHUO_SHORT_NAME = 'taohui'

DOMAIN = 'http://taohui.org.cn'
DB_NAME = 'blog'
DB_USER = 'root'
DB_PWD = 'iamtaohui'
