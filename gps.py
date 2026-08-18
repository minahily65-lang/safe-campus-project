# gps.py

import random
from datetime import datetime


class GPS:

    @staticmethod
    def get_current_location():
        """
        Simulated GPS location.
        Replace this later with a real GPS or geolocation API.
        """

        latitude = round(random.uniform(24.80, 24.95), 6)
        longitude = round(random.uniform(67.00, 67.20), 6)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "location": f"{latitude}, {longitude}",
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }