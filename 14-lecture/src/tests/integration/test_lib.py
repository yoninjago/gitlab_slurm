"""
This file (test_lib.py) contains the integration tests for the features.py file.
"""
from datetime import datetime
import os
from application import create_app


def test_date():
    """Tests the date functionality."""
    flask_app = create_app()
    now = datetime.now()
    current_date = now.strftime("%m/%d/%Y")
    with flask_app.test_client() as test_client:
        response = test_client.get("/")
        data = response.data.decode()
        assert response.status_code == 200
        assert "Current time" in data
        assert current_date in data


def test_version():
    """Tests the version functionality."""
    flask_app = create_app()
    ci_test = bool(os.getenv("CI", "Undefined") != "Undefined")
    version = os.getenv("VERSION", "N/A")
    with flask_app.test_client() as test_client:
        response = test_client.get("/version")
        data = response.data.decode()
        assert response.status_code == 200
        assert f"Application version {version}" in data
        assert f"Running from CI: {str(ci_test)}" in data
