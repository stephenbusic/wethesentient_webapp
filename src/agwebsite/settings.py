# Django settings file
import os
from . import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Build base DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Django's Secret Key
SECRET_KEY = config.secret_key

# Key for encryption
ENCRYPT_KEY = config.encrypt_key['key']

# Recaptcha Secret Key
if not DEBUG:
    # Keys for Production
    RECAPTCHA_SITE_KEY = config.reCAPTCHA['site_key']
    RECAPTCHA_SECRET_KEY = config.reCAPTCHA['secret_key']
else:
    # Keys for Local Testing
    RECAPTCHA_SITE_KEY = config.reCAPTCHA_LOCALTESTING['site_key']
    RECAPTCHA_SECRET_KEY = config.reCAPTCHA_LOCALTESTING['secret_key']


# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'


# Apply these security settings only if DEBUG
# is false, since they break the site locally
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    ALLOWED_HOSTS = ['www.aaahhhghosts.com']
else:
    ALLOWED_HOSTS = ['127.0.0.1']


# Email Settings
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = config.gmail['address']
EMAIL_HOST_PASSWORD = config.gmail['pword']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'homepage',
    'posts',
    'follow',
    'users',
    'analytical',
    'django_inlinecss',
    'ckeditor',
    'ckeditor_uploader',
    'groupadmin_users',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.facebook',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agwebsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'agwebsite.wsgi.application'


# Use MySql if in Production
if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config.AGmySQL['name'],
            'USER': config.AGmySQL['user'],
            'PASSWORD': config.AGmySQL['pword'],
            'HOST': config.AGmySQL['host'],
            'TEST': {
                'NAME': config.AGmySQL['testname'],
            },
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }

# Else if testing locally, use SQLite
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# Password validation
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

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile',],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.12',
    },

     'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },

    'twitter': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'include_email': True,
        }
    },

}


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
VENV_PATH = os.path.dirname(BASE_DIR)
STATIC_ROOT = os.path.join(VENV_PATH, 'static_root')
MEDIA_ROOT = os.path.join(VENV_PATH, 'media_root')


# --- CKeditor Settings ---
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default': {
       'toolbar_Full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['SpecialChar'], ['Source'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Font', 'Subscript', 'Superscript'],
            ['NumberedList', 'BulletedList'],
            ['Indent', 'Outdent'],
            ['Maximize'],
        ],
    },
    'extraPlugins': ','.join(['tab','justify','liststyle','indent','uploadimage']),
    'tabSpaces': 4,
}


# --- Django Analytical Settings ---
CLICKY_SITE_ID = config.analytical['clicky_ID']
CRAZY_EGG_ACCOUNT_NUMBER = config.analytical['crazyegg_Num']


# --- AllAuth Settings ---
# Disable new users signup
# look at users/adapter.py
ACCOUNT_ADAPTER = 'users.adapter.NoNewUsersAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapter.YesNewUsersSocialAccountAdapter'

# redirects to profile page if not configured.
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

SITE_ID = 1
