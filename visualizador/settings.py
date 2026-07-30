import os
import stat
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_secret_key():
    """
    Resolve SECRET_KEY without ever committing one to the repository.

    Order of preference:
      1. DJANGO_SECRET_KEY environment variable (use this in production).
      2. A generated key cached in BASE_DIR/.secret_key (gitignored), so that
         `git clone && python manage.py runserver` works with no setup and the
         key stays stable across restarts and across worker processes.
      3. An ephemeral in-memory key, if the cache file cannot be written.

    Step 2 matters for correctness as much as for secrecy: a per-process random
    key would make CSRF tokens issued by one worker fail validation on another.
    """
    key = os.environ.get('DJANGO_SECRET_KEY')
    if key:
        return key

    key_file = BASE_DIR / '.secret_key'
    try:
        if key_file.exists():
            cached = key_file.read_text(encoding='utf-8').strip()
            if cached:
                return cached
    except OSError:
        pass

    key = get_random_secret_key()
    try:
        key_file.write_text(key, encoding='utf-8')
        # Owner-only where the platform honours it (no-op on Windows).
        os.chmod(key_file, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        # Read-only filesystem: fall back to an ephemeral key. Single-worker
        # deployments still work; multi-worker ones must set the env var.
        pass
    return key


SECRET_KEY = _load_secret_key()
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