from database import (
    create_sos,
    get_all_alerts,
    update_alert_status,
    delete_alert,
)


# =========================================================
# GOOGLE MAPS LINK
# =========================================================

def create_google_maps_link(latitude, longitude):

    return (
        f"https://www.google.com/maps/search/"
        f"?api=1&query={latitude},{longitude}"
    )


# =========================================================
# SEND SOS ALERT
# =========================================================

def send_sos_alert(user, location):

    try:

        # Google Maps link
        maps_link = create_google_maps_link(
            location["latitude"],
            location["longitude"]
        )

        # Save SOS in MongoDB
        alert_id = create_sos(
            student_id=user["_id"],
            student_name=user["name"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )

        if alert_id is None:
            return None

        print("SOS Alert Saved")
        print("Google Maps:", maps_link)

        return {
            "success": True,
            "alert_id": str(alert_id),
            "student_name": user["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "google_maps_link": maps_link,
            "status": "Pending",
        }

    except Exception as error:

        print("SOS Alert Error:", error)

        return None


# =========================================================
# GET ALL SOS ALERTS
# =========================================================

def get_sos_alerts():

    try:
        return get_all_alerts()

    except Exception as error:

        print("Get SOS Alerts Error:", error)

        return []


# =========================================================
# UPDATE ALERT STATUS
# =========================================================

def change_alert_status(alert_id, status):

    try:

        return update_alert_status(
            alert_id,
            status
        )

    except Exception as error:

        print("Update Alert Error:", error)

        return False


# =========================================================
# DELETE ALERT
# =========================================================

def remove_alert(alert_id):

    try:

        return delete_alert(alert_id)

    except Exception as error:

        print("Delete Alert Error:", error)

        return False