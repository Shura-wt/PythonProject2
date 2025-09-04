try:
    # When running from the outer 'api' directory (uwsgi.ini alongside), import inner app as 'api.app'
    from api.app import app as application  # type: ignore
except ModuleNotFoundError:
    # Fallback when running from project root where outer package name is 'api'
    from api.api.app import app as application  # type: ignore

from werkzeug.middleware.proxy_fix import ProxyFix
application.wsgi_app = ProxyFix(application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

