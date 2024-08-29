"""
Django settings for fish_bowl_project project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import environ
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 업로드된 파일이 저장될 디렉토리 경로 설정
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 업로드된 파일에 접근할 수 있는 URL 경로 설정
MEDIA_URL = '/media/'


environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "llm",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fish_bowl_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "fish_bowl_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # 정적 파일 경로 설정
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")   # 배포를 위한 정적 파일 경로

# # Media files (Uploads)
# MEDIA_URL = "/media/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



# settings.py

# 세션 엔진 설정 (디폴트는 DB 세션)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # DB에 세션 저장
# 또는 파일 기반 세션 사용
# SESSION_ENGINE = 'django.contrib.sessions.backends.file'

# 세션이 유지되는 기간 (초)
SESSION_COOKIE_AGE = 1209600  # 2주 (기본값)

# 세션 쿠키 설정
SESSION_COOKIE_NAME = 'sessionid'  # 쿠키의 이름 (기본값)
SESSION_COOKIE_SECURE = False  # HTTPS를 통해서만 쿠키가 전송되도록 설정 (개발 중일 경우 False)

# 세션 쿠키가 클라이언트에 저장된 이후의 보안 설정
SESSION_COOKIE_HTTPONLY = True  # 자바스크립트에서 세션 쿠키에 접근하지 못하도록 설정

# 세션이 만료될 때 자동으로 삭제되는지 여부
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # 브라우저가 닫히면 세션이 만료되지 않도록 설정

# 세션의 만료일을 갱신할지 여부
SESSION_SAVE_EVERY_REQUEST = False  # 세션이 변경되지 않더라도 매 요청마다 갱신되지 않도록 설정

# 세션 파일을 저장할 경로 (파일 기반 세션을 사용할 경우 필요)
# SESSION_FILE_PATH = '/your/file/path/here'
