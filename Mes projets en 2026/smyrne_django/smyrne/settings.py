"""
=============================================================
SETTINGS — Projet Django 5e CELPA SMYRNE
=============================================================
Configuration complète pour le développement et la production.
"""

import os
from pathlib import Path
import environ

# ─────────────────────────────────────────
# Répertoires de base
# ─────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger les variables depuis le fichier .env
env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1', 'testserver']),
)
environ.Env.read_env(BASE_DIR / '.env')

# ─────────────────────────────────────────
# Sécurité
# ─────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ─────────────────────────────────────────
# Applications installées
# ─────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Packages tiers
    'ckeditor',
    'ckeditor_uploader',
    'axes',
    # Applications du projet Smyrne
    'apps.core',
    'apps.cultes',
    'apps.predications',
    'apps.articles',
    'apps.evenements',
    'apps.galerie',
    'apps.priere',
    'apps.histoire',
    'apps.ministeres',
    'apps.accounts',
]

# ─────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

# ─────────────────────────────────────────
# URLs et WSGI
# ─────────────────────────────────────────
ROOT_URLCONF = 'smyrne.urls'
WSGI_APPLICATION = 'smyrne.wsgi.application'

# ─────────────────────────────────────────
# Templates
# ─────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.parametres_site',
            ],
        },
    },
]

# ─────────────────────────────────────────
# Base de données
# ─────────────────────────────────────────
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# ─────────────────────────────────────────
# Validation des mots de passe
# ─────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────
# Internationalisation
# ─────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────
# Fichiers statiques
# ─────────────────────────────────────────
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# En développement : stockage simple sans compression
# En production : WhiteNoise avec compression et cache
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─────────────────────────────────────────
# Médias (images, vidéos, audio uploadés)
# ─────────────────────────────────────────
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────────────────
# Clé primaire par défaut
# ─────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────
# Authentification et sessions
# ─────────────────────────────────────────
LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ─────────────────────────────────────────
# Sécurité en production uniquement
# ─────────────────────────────────────────
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ─────────────────────────────────────────
# Cache système (utilisé pour rate limiting & sessions)
# ─────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'smyrne-cache',
    }
}

# ─────────────────────────────────────────
# Configuration CKEditor (éditeur WYSIWYG)
# ─────────────────────────────────────────
CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'HorizontalRule'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
            ['Source'],
        ],
        'height': 400,
        'width': '100%',
        'removePlugins': 'stylesheetparser',
        'language': 'fr',
    },
    'basic': {
        'toolbar': 'Basic',
        'height': 200,
        'width': '100%',
        'language': 'fr',
    },
}

# ─────────────────────────────────────────
# Django Axes (Anti-brute-force)
# ─────────────────────────────────────────
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_TEMPLATE = None
AXES_RESET_ON_SUCCESS = True
# En développement : ne pas bloquer localhost; en production : bloquer normalement
AXES_NEVER_LOCKOUT_WHITELIST = env.bool('AXES_NEVER_LOCKOUT_WHITELIST', default=DEBUG)
AXES_IP_WHITELIST = ['127.0.0.1', '::1']

# Backends d'authentification (Axes doit être en premier)
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ─────────────────────────────────────────
# Journalisation (Logging)
# ─────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'axes': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# ─────────────────────────────────────────
# Titre de l'interface d'administration
# ─────────────────────────────────────────
ADMIN_SITE_HEADER = '5e CELPA SMYRNE — Administration'
ADMIN_SITE_TITLE = 'Smyrne Admin'
ADMIN_INDEX_TITLE = 'Tableau de bord'
