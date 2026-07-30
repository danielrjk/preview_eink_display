import os
import stat
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_list(name, default):
    """Read a comma-separated environment variable into a list."""
    raw = os.environ.get(name, '')
    return [item.strip() for item in raw.split(',') if item.strip()] or default


def _load_secret_key():
    """
    Resolve SECRET_KEY without ever committing one to the repository.

    Order of preference:
      1. DJANGO_SECRET_KEY environment variable (use this in production).
      2. A generated key cached in BASE_DIR/.secret_key (gitignored), so that
         `git clone && python manage.py runserver` works with no setup and the
         key stays stable across restarts and across worker processes.
      3. An ephemeral in-memory key, if the cache file cannot be written.

    Step 2 matters for correctness as much as for secrecy: workers must agree
    on the key, or a CSRF token issued by one fails validation on another.

    Which is why the write is exclusive rather than a plain write_text. Several
    workers starting at once with no cache file present would each generate a
    different key and race; the file would hold whichever wrote last, but every
    process would keep returning the key it generated itself, and they would
    disagree until all of them restarted. O_CREAT | O_EXCL means exactly one
    process creates the file, and the losers read back the winner's key instead
    of using their own.
    """
    key = os.environ.get('DJANGO_SECRET_KEY')
    if key:
        return key

    key_file = BASE_DIR / '.secret_key'

    def read_cached():
        try:
            cached = key_file.read_text(encoding='utf-8').strip()
        except OSError:
            return None
        return cached or None

    cached = read_cached()
    if cached:
        return cached

    key = get_random_secret_key()
    try:
        # Exclusive create: fails if another process got there first.
        fd = os.open(key_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        # Lost the race. The winner's key is the one everyone must use.
        return read_cached() or key
    except OSError:
        # Read-only filesystem: fall back to an ephemeral key. Single-worker
        # deployments still work; multi-worker ones must set the env var.
        return key

    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(key)
    except OSError:
        return key
    return key


SECRET_KEY = _load_secret_key()
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