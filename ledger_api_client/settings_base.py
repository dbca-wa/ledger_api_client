from django.core.exceptions import ImproperlyConfigured
from confy import env, database
import sys
import dj_database_url
import os

# Project paths
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = None
BASE_DIR_ENV = env('BASE_DIR',None)
if BASE_DIR_ENV is None:
   BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
else:
   BASE_DIR = BASE_DIR_ENV
PROJECT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ledger')

PAYMENT_OFFICERS_GROUP = env('PAYMENT_OFFICERS_GROUP','Payments Officers')

LEDGER_API_KEY=env('LEDGER_API_KEY',"NO_KEY_PROVIDED")
LEDGERGW_URL=env('LEDGERGW_URL','http://localhost/')
LEDGER_API_URL=env('LEDGER_API_URL','http://localhost/')
LEDGER_UI_URL=env('LEDGER_UI_URL','http://localhost/')

# Application definitions
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', False)
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', False)
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = env('ALLOWED_HOSTS', [])
WSGI_APPLICATION = 'ledger.wsgi.application'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
#    'django.contrib.flatpages',
    'django_extensions',
    'widget_tweaks',
    'django_countries',
    'django_cron',
]

PASSWORD_HASHERS = [ 
            'ledger_api_client.auth_hashers.PBKDF2PasswordHasher',
            ]


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ledger_api_client.middleware.SSOLoginMiddleware',
    #'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

# Authentication settings
LOGIN_URL = '/'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_USER_MODEL = 'ledger_api_client.EmailUserRO'
# for reference, django.conf.settings.X == backend.setting('X')
# this one prevents the email auth backend from creating EmailUsers with a username param
USER_FIELDS = ['email']

SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN', None)
if SESSION_COOKIE_DOMAIN:
    SESSION_COOKIE_NAME = (SESSION_COOKIE_DOMAIN + ".ledger_sessionid").replace(".", "_")


# Email settings
ADMINS = ('asi@dpaw.wa.gov.au',)
EMAIL_HOST = env('EMAIL_HOST', 'email.host')
EMAIL_PORT = env('EMAIL_PORT', 25)
EMAIL_FROM = env('EMAIL_FROM', ADMINS[0])
DEFAULT_FROM_EMAIL = EMAIL_FROM

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ledger_api_client.context_processors.config'
            ],
        },
    },
]


BOOTSTRAP3 = {
    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    #'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
    'base_url': '/static/ledger/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'required_css_class': 'required-form-field',
    'set_placeholder': False,
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}


## Database
#DATABASES = {
#    # Defined in the DATABASE_URL env variable.
#    'default': database.config(),
#}

#DATABASE_ROUTERS = ['ledger.payments.models.OracleFinanceDBRouter']
DATABASE_ROUTERS = ['ledger_api_client.ledger_models.LedgerDBRouter',]
DATABASE_APPS_MAPPING = {
    'contenttypes': 'default',
    'auth': 'default',
    'admin': 'default',
    'sessions': 'default',
    'messages': 'default',
    'staticfiles': 'default',
    'ledger_api_client': 'default', 
}

# Database
DATABASES = {
    # Defined in the DATABASE_URL env variable.
    'default': database.config(),
}
if len(sys.argv) > 1:
    if sys.argv[1] == 'makemigrations' or sys.argv[1] == 'migrate':
        print ("Skipping ledger_db")
        pass
    else: 
        DATABASES['ledger_db'] =  dj_database_url.config(env='LEDGER_DATABASE_URL')
else:
    DATABASES['ledger_db'] =  dj_database_url.config(env='LEDGER_DATABASE_URL')





# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
#LANGUAGE_CODE = 'en-AU'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
#    os.path.join(os.path.join(PROJECT_DIR, 'static')),
# Removed as these should be in the individual app settings.py and not in ledger.
# leaving hashed in case issues are caused by this.
#    os.path.join(os.path.join(BASE_DIR, 'wildlifelicensing', 'static')),
#    os.path.join(os.path.join(BASE_DIR, 'wildlifecompliance', 'static')),
]
if not os.path.exists(os.path.join(BASE_DIR, 'media')):
    os.mkdir(os.path.join(BASE_DIR, 'media'))
MEDIA_ROOT = env('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

# Logging settings
# Ensure that the logs directory exists:
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.mkdir(os.path.join(BASE_DIR, 'logs'))
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': env('LOG_CONSOLE_LEVEL', 'INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'ledger.log'),
            'formatter': 'verbose',
            'maxBytes': 5242880
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': env('LOG_CONSOLE_LEVEL', 'WARNING'),
            'propagate': True
        },
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'log': {
            'handlers': ['file'],
            'level': 'INFO'
        },
        'wildlifelicensing': {
            'handlers': ['file'],
            'level': 'INFO'
        },
        'wildlifecompliance': {
            'handlers': ['file'],
            'level': 'INFO'
        },
        'disturbance': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        },
#        'oscar.checkout': {
#            'handlers': ['file'],
#            'level': 'INFO'
#        },
#        'bpoint_dpaw': {
#            'handlers': ['file'],
#            'level': 'INFO'
#        }
    }
}

# django-dynamic-fields test generation settings
DDF_FILL_NULLABLE_FIELDS = False

# Ledger settings
CMS_URL=env('CMS_URL',None)
VALID_SYSTEMS=env('VALID_SYSTEMS', '')
VALID_SYSTEMS=VALID_SYSTEMS.split(',') if VALID_SYSTEMS else []
LEDGER_USER=env('LEDGER_USER',None)
LEDGER_PASS=env('LEDGER_PASS')
NOTIFICATION_EMAIL=env('NOTIFICATION_EMAIL')
BPAY_GATEWAY = env('BPAY_GATEWAY', None)
INVOICE_UNPAID_WARNING = env('INVOICE_UNPAID_WARNING', '')
# GST Settings
LEDGER_GST = env('LEDGER_GST',10)
# BPAY settings
BPAY_ALLOWED = env('BPAY_ALLOWED',True)
BPAY_BILLER_CODE=env('BPAY_BILLER_CODE')
# BPOINT settings
BPOINT_CURRENCY='AUD'
BPOINT_BILLER_CODE=env('BPOINT_BILLER_CODE')
BPOINT_USERNAME=env('BPOINT_USERNAME')
BPOINT_PASSWORD=env('BPOINT_PASSWORD')
BPOINT_MERCHANT_NUM=env('BPOINT_MERCHANT_NUM')
BPOINT_TEST=env('BPOINT_TEST',True)
# Custom Email Settings
EMAIL_BACKEND = 'ledger_api_client.ledger_email.LedgerEmailBackend'
PRODUCTION_EMAIL = env('PRODUCTION_EMAIL', False)
# Intercept and forward email recipient for non-production instances
# Send to list of NON_PROD_EMAIL users instead
EMAIL_INSTANCE = env('EMAIL_INSTANCE','PROD')
NON_PROD_EMAIL = env('NON_PROD_EMAIL')

if not PRODUCTION_EMAIL:
    if not NON_PROD_EMAIL:
        raise ImproperlyConfigured('NON_PROD_EMAIL must not be empty if PRODUCTION_EMAIL is set to False')
    if EMAIL_INSTANCE not in ['PROD','DEV','TEST','UAT']:
        raise ImproperlyConfigured('EMAIL_INSTANCE must be either "PROD","DEV","TEST","UAT"')
    if EMAIL_INSTANCE == 'PROD':
        raise ImproperlyConfigured('EMAIL_INSTANCE cannot be \'PROD\' if PRODUCTION_EMAIL is set to False')

PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE=env('PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE','')
PAYMENT_INTERFACE_SYSTEM_ID=env('PAYMENT_INTERFACE_SYSTEM_ID','')
SESSION_EXPIRY_SSO = 883600
ENABLE_DJANGO_LOGIN=env('ENABLE_DJANGO_LOGIN', False)

LEDGER_UI_ACCOUNTS_MANAGEMENT = [
            # {'account_name': {'options' : {'view': True, 'edit': True}}},
            # {'legal_name': {'options' : {'view': True, 'edit': True}}},
            # {'verified_legal_name': {'options' : {'view': True, 'edit': True}}},

            {'first_name': {'options' : {'view': True, 'edit': True}}},
            {'last_name': {'options' : {'view': True, 'edit': True}}},
            #{'legal_first_name': {'options' : {'view': True, 'edit': True}}},
            #{'legal_last_name': {'options' : {'view': True, 'edit': True}}},
            {'dob': {'options' : {'view': True, 'edit': True}}},
 
            #{'identification': {'options' : {'view': True, 'edit': True}}},

            {'residential_address': {'options' : {'view': True, 'edit': True}}},
            {'postal_address': {'options' : {'view': True, 'edit': True}}},
            {'postal_same_as_residential': {'options' : {'view': True, 'edit': True}}},

            #{'postal_address': {'options' : {'view': True, 'edit': True}}},
            {'phone_number' : {'options' : {'view': True, 'edit': True}}},
            {'mobile_number' : {'options' : {'view': True, 'edit': True}}},

]
LEDGER_UI_CARDS_MANAGEMENT = False

LEDGER_UI_ACCOUNTS_MANAGEMENT_KEYS = []
for am in LEDGER_UI_ACCOUNTS_MANAGEMENT:
    LEDGER_UI_ACCOUNTS_MANAGEMENT_KEYS.append(list(am.keys())[0])
