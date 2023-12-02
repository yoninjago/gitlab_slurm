"""Main application code represents its routes"""

from flask import Flask
from .lib.features import Site


def create_app():
    """Creates an app"""
    app = Flask(__name__)
    init(app)
    return app


def init(app):
    """Inits the app"""
    site = Site()
    current_version = Site.get_version(site)
    is_ci = str(Site.get_ci(site))

    @app.route("/")
    def time():
        return f"<h1>Current time</h1><h2>{Site.get_ntp_time(site)}</h2>"

    @app.route("/version")
    def version():
        return f"<h1>Application version {current_version}</h1><h2>Running from CI: {is_ci}</h2>"
