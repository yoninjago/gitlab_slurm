"""
This file (test_features.py) contains the unit tests for the features.py file.
"""
from datetime import datetime
import os
from application.lib.features import Site


def test_time():
    """Tests the time valid value."""
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y %H:%M")
    test_time = Site().get_ntp_time()
    assert current_time == test_time


def test_version():
    """Tests the version valid value."""
    version = os.getenv("VERSION", "N/A")
    test_version = Site().get_version()
    assert version == test_version


def test_ci():
    """Tests the CI valid value."""
    os.environ["CI"] = ""
    site = Site()
    ci_test = site.get_ci()
    assert not ci_test
    os.environ["CI"] = "gitlab"
    site = Site()
    ci_test = site.get_ci()
    assert ci_test
