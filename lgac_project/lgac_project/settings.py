import os
from pathlib import Path
from dotenv import load_dotenv

# =====================================================
# BASE / ENV
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ENVIRONMENT = os.getenv("ENVIRONMENT", "staging").lower()

def env_bool(key, default=False):
    return os.getenv(key, str(default)).lower() in ("1", "true", "yes")

# =====================================================
# CORE SETTINGS
# =====================================================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in environment")

DEBUG = env_bool("DEBUG", ENVIRONMENT != "production")
#DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
    "192.168.0.136",
    "akuresouthlga.on.gov.ng",
    "www.akuresouthlga.on.gov.ng",
#    "*"
]

SITE_URL = os.getenv(
    "SITE_URL",
    "http://127.0.0.1:8000" if ENVIRONMENT != "production" else "https://akuresouthlga.on.gov.ng"
)

STATE_NAME = os.getenv("STATE_NAME", "Ondo")


# =====================================================
# SECURITY (ENVIRONMENT AWARE â€“ SINGLE SOURCE OF TRUTH)
# =====================================================
if ENVIRONMENT == "production":
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    CSRF_TRUSTED_ORIGINS = [
        "https://akuresouthlga.on.gov.ng",
        "https://www.akuresouthlga.on.gov.ng",
    ]

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # STAGING / LOCAL
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    CSRF_TRUSTED_ORIGINS = []
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# =====================================================
# APPLICATIONS
# =====================================================
INSTALLED_APPS = [
    # Django
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "crispy_forms",
    "axes",

    # Local apps
    "apps.accounts",
    "apps.applications",
    "apps.lgas",
    "apps.payments",
    "apps.core",
]

AUTH_USER_MODEL = "accounts.User"

# =====================================================
# MIDDLEWARE
# =====================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",  
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =====================================================
# AUTHENTICATION
# =====================================================
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "apps.accounts.auth_backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# =====================================================
# URL / TEMPLATES
# =====================================================
ROOT_URLCONF = "lgac_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lgac_project.wsgi.application"

# =====================================================
# DATABASE
# =====================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST", "localhost"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}

# =====================================================
# PASSWORD VALIDATION
# =====================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =====================================================
# INTERNATIONALIZATION
# =====================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# =====================================================
# STATIC & MEDIA
# =====================================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =====================================================
# AXES (LOGIN PROTECTION)
# =====================================================
AXES_ENABLED = ENVIRONMENT == "production"
AXES_FAILURE_LIMIT = 5
AXES_LOCK_OUT_AT_FAILURE = True
AXES_COOLOFF_TIME = 1  # hours
AXES_RESET_ON_SUCCESS = True

# DO NOT protect admin URLs with Axes
AXES_EXCLUDE_URLS = [
    r"^/admin/.*",
    r"^/accounts/ping/$",
]

# =====================================================
# VERIFYME
# =====================================================
VERIFYME_API_KEY = os.getenv("VERIFYME_API_KEY")

# =====================================================
# PAYSTACK
# =====================================================
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

PAYSTACK_INIT_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"

# =====================================================
# EMAIL
# =====================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

# =====================================================
# LOGGING
# =====================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# ==========================
# JAZZMIN ADMIN CONFIG
# ==========================

JAZZMIN_SETTINGS = {
    # Site identity
    "site_title": "Ondo State LGAC",
    "site_header": "Ondo State LGAC Portal",
    "site_brand": "LGAC Portal",

    # Logos (keep these minimal – sizing handled in CSS)
    "site_logo": "img/ondo_logo.png",
    "login_logo": "img/ondo_logo.png",
    "site_icon": "img/ondo_logo_small.png",

    # IMPORTANT: do NOT use img-circle for government branding
    "site_logo_classes": "",

    # Custom CSS (single source of truth)
    "custom_css": "css/admin-custom.css",

    # Welcome text
    "welcome_sign": "Welcome to Ondo State LGAC Administration",

    # Top menu
    "topmenu_links": [
        {
            "name": "Dashboard",
            "url": "admin:index",
            "permissions": ["auth.view_user"],
        },
        {
            "name": "Public Portal",
            "url": "/",
            "new_window": True,
        },
    ],

    # Sidebar behaviour
    "show_sidebar": True,
    "navigation_expanded": True,

    # Form layout
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
    },

    # Footer (ASCII-safe, avoids encoding issues)
    "footer_text": "Ondo State Government - Ministry of Local Government",

    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "applications.Application": "fas fa-file-alt",
        "payments.Payment": "fas fa-credit-card",
        "lga.LGA": "fas fa-landmark",
    },
}


# ==========================
# JAZZMIN UI TWEAKS
# ==========================

JAZZMIN_UI_TWEAKS = {
    # Theme
    "theme": "flatly",            # clean, government-friendly
    "dark_mode_theme": "darkly",

    # Branding colours
    "navbar": "navbar-dark",
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",

    # Sidebar
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,

    # Buttons
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# =========================================
# Auto logout after 5 minutes of inactivity
# =========================================

SESSION_COOKIE_AGE = 300          # 5 minutes
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
