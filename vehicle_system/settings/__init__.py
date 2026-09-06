import environ

_env = environ.Env()
_django_env = _env.str("DJANGO_ENV", default="development")

if _django_env == "production":
    from .production import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403
