"""Conftest to configure the test suite"""

import pytest
from application import create_app


@pytest.fixture(scope="module")
def test_client():
    """Tests the client"""
    flask_app = create_app()

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!
