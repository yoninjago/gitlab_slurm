"""Defines our application Site class"""
import os
import time
import ntplib


class Site:
    """
    Class that represents a Site
    """

    def __init__(self):
        """Create a new Site object with some predefined attributes"""
        client = ntplib.NTPClient()
        response = client.request("pool.ntp.org")
        self.time = time.strftime("%m/%d/%Y %H:%M", time.localtime(response.tx_time))
        self.version = os.getenv("VERSION", "N/A")
        self.is_ci = os.getenv("CI", "Undefined")

    def get_ntp_time(self):
        """returns time"""
        return self.time

    def get_version(self):
        """returns version"""
        return self.version

    def get_ci(self):
        """returns if the site is running inside the CI"""
        return bool(self.is_ci != "Undefined" and self.is_ci)
