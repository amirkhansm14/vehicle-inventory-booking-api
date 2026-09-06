import environ

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DATABASE_URL = env.str("DATABASE_URL", default="") or f"sqlite:///{BASE_DIR / 'db.sqlite3'}"  # noqa: F405
DATABASES = {"default": environ.Env.db_url_config(DATABASE_URL)}

REST_FRAMEWORK = {  # noqa: F405
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}
