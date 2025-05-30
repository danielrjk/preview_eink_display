from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'uk$bp#35(%--2ozl%3^=&d!!hzoy5^!b364&3y&%p76)p5!mh0'
DEBUG = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'app',  # Adicione seu app principal
]

MIDDLEWARE = []

ROOT_URLCONF = 'visualizador.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Diretório para templates
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]

WSGI_APPLICATION = None  # Remova se não for usar WSGI
DATABASES = {}

FORCE_SCRIPT_NAME = '/eink_visualizer'
STATIC_URL = '/eink_visualizer/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}