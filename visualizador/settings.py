import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_list(name, default):
    """Read a comma-separated environment variable into a list."""
    raw = os.environ.get(name, '')
    return [item.strip() for item in raw.split(',') if item.strip()] or default


SECRET_KEY = 'uk$bp#35(%--2ozl%3^=&d!!hzoy5^!b364&3y&%p76)p5!mh0'
DEBUG = False

# Was ['*'], which accepts any Host header. Override with a comma-separated
# DJANGO_ALLOWED_HOSTS when deploying somewhere other than the hosts below.
ALLOWED_HOSTS = _env_list(
    'DJANGO_ALLOWED_HOSTS',
    ['localhost', '127.0.0.1', '[::1]', 'kielma.dev.br'],
)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'app',  # Adicione seu app principal
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- CSRF / transport hardening -------------------------------------------
# /process-code executes submitted code, so an unauthenticated cross-origin
# POST is the whole attack. CsrfViewMiddleware above is what closes it; the
# settings here keep it working correctly behind TLS and reverse proxies.

# Django validates the Origin header of an https request against this list.
# Behind a proxy Django only knows the request is https via
# SECURE_PROXY_SSL_HEADER below, so both are needed to avoid spurious 403s.
CSRF_TRUSTED_ORIGINS = _env_list(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    ['https://kielma.dev.br'],
)

# Set DJANGO_BEHIND_PROXY=1 when a reverse proxy terminates TLS, so Django
# sees the request as https and the Origin check above matches.
if os.environ.get('DJANGO_BEHIND_PROXY') == '1':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Off by default so plain-http local development still works. Set
# DJANGO_SECURE_COOKIES=1 on any HTTPS deployment.
if os.environ.get('DJANGO_SECURE_COOKIES') == '1':
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# The page injects the token via {{ csrf_token }} rather than reading the
# cookie, so JavaScript never needs access to it.
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

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