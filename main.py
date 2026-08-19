import os

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from database import (
    login_user,
    register_user,
    get_user_by_email,
    get_user_by_id,
    get_all_users,
    get_all_alerts,
    get_history,
    delete_user,
    update_alert_status,
    save_history,
)
from pubsub import send_sos_alert
from gps import GPS
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "safe-campus-change-this-secret-key")


def login_required(role=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                if request.path.startswith("/api/"):
                    return jsonify(success=False, message="Login required."), 401
                return redirect(url_for("login_page"))

            user = get_user_by_id(session["user_id"])
            if user is None:
                session.clear()
                if request.path.startswith("/api/"):
                    return jsonify(success=False, message="Login required."), 401
                return redirect(url_for("login_page"))

            if role and user.get("role") != role:
                if request.path.startswith("/api/"):
                    return jsonify(success=False, message="Access denied."), 403
                return "Access Denied", 403

            return view(user, *args, **kwargs)
        return wrapped
    return decorator


@app.get("/")
def splash_page():
    # Starting the app always begins with Splash -> Login.
    session.clear()
    return render_template("splash.html")


@app.get("/login")
def login_page():
    return render_template("login.html")


@app.post("/login")
def login_api():
    try:
        data = request.get_json(silent=True) or request.form
        email = str(data.get("email", "")).strip()
        password = str(data.get("password", "")).strip()

        if not email or not password:
            return jsonify(success=False, message="Please fill all fields."), 400

        user = login_user(email, password)
        if not user:
            return jsonify(success=False, message="Invalid email or password."), 401

        role = user.get("role")
        role_urls = {
            "Student": url_for("student_dashboard"),
            "Security": url_for("security_dashboard"),
            "Admin": url_for("admin_dashboard"),
        }
        if role not in role_urls:
            return jsonify(success=False, message="Invalid user role."), 403

        session.clear()
        session["user_id"] = str(user["_id"])
        session["role"] = role
        return jsonify(success=True, message="Login Successful!", role=role, redirect=role_urls[role])
    except Exception as exc:
        print("LOGIN ERROR:", exc)
        return jsonify(success=False, message="An error occurred while logging in."), 500


@app.get("/register")
def register_page():
    return render_template("register.html")


@app.post("/register")
def register_api():
    try:
        data = request.get_json(silent=True) or request.form
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        phone = str(data.get("phone", "")).strip()
        password = str(data.get("password", "")).strip()
        role = str(data.get("role", "")).strip()

        if not all([name, email, phone, password, role]):
            return jsonify(success=False, message="Please fill all fields."), 400
        if role not in {"Student", "Security", "Admin"}:
            return jsonify(success=False, message="Invalid role selected."), 400
        if get_user_by_email(email):
            return jsonify(success=False, message="Email already exists."), 409
        if not register_user(name, email, phone, password, role):
            return jsonify(success=False, message="Registration failed."), 500

        return jsonify(success=True, message="Registration Successful!", redirect=url_for("login_page"))
    except Exception as exc:
        print("REGISTRATION ERROR:", exc)
        return jsonify(success=False, message="An error occurred during registration."), 500


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.get("/student")
@login_required("Student")
def student_dashboard(user):
    return render_template("student.html", user=user)


@app.post("/api/student/sos")
@login_required("Student")
def student_sos(user):
    try:
        data = request.get_json(silent=True) or {}
        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat is None or lon is None:
            location = GPS.get_current_location()
        else:
            location = {"latitude": float(lat), "longitude": float(lon)}

        if not location or location.get("latitude") is None or location.get("longitude") is None:
            return jsonify(success=False, message="Could not determine your location."), 400

        alert = send_sos_alert(user, location)
        if not alert:
            return jsonify(success=False, message="Could not send SOS alert."), 500
        return jsonify(**alert)
    except Exception as exc:
        print("SOS ERROR:", exc)
        return jsonify(success=False, message="An error occurred while sending SOS."), 500


@app.post("/api/student/location")
@login_required("Student")
def student_location(user):
    try:
        data = request.get_json(silent=True) or {}
        lat = data.get("latitude")
        lon = data.get("longitude")
        location = (
            GPS.get_current_location()
            if lat is None or lon is None
            else {"latitude": float(lat), "longitude": float(lon)}
        )
        if not location:
            return jsonify(success=False, message="Location unavailable."), 400

        latitude = location["latitude"]
        longitude = location["longitude"]
        maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
        return jsonify(success=True, latitude=latitude, longitude=longitude, maps_url=maps_url)
    except Exception as exc:
        print("LOCATION ERROR:", exc)
        return jsonify(success=False, message="Could not get location."), 500


@app.get("/api/history")
def history_api():
    if "user_id" not in session:
        return jsonify(success=False, message="Login required."), 401
    try:
        return jsonify(success=True, history=[serialize_doc(x) for x in get_history()])
    except Exception as exc:
        print("HISTORY ERROR:", exc)
        return jsonify(success=False, message="Could not load history."), 500


@app.get("/security")
@login_required("Security")
def security_dashboard(user):
    return render_template("security.html", user=user)


@app.get("/api/security/alerts")
@login_required("Security")
def security_alerts(user):
    try:
        return jsonify(success=True, alerts=[serialize_doc(x) for x in get_all_alerts()])
    except Exception as exc:
        print("SECURITY ALERT ERROR:", exc)
        return jsonify(success=False, message="Could not load alerts."), 500


@app.post("/api/security/alerts/<alert_id>/resolve")
@login_required("Security")
def resolve_alert(user, alert_id):
    try:
        data = request.get_json(silent=True) or {}
        remarks = str(data.get("remarks", "Resolved by security staff")).strip()
        alert = next((x for x in get_all_alerts() if str(x.get("_id")) == str(alert_id)), None)
        if not alert:
            return jsonify(success=False, message="Alert not found."), 404

        if not update_alert_status(alert_id, "Resolved"):
            return jsonify(success=False, message="Could not update alert status."), 500

        save_history(
            alert_id=alert_id,
            student_name=alert.get("student_name", "Unknown"),
            security_name=user.get("name", "Security"),
            latitude=alert.get("latitude"),
            longitude=alert.get("longitude"),
            remarks=remarks,
        )
        return jsonify(success=True, message="Alert resolved successfully.")
    except Exception as exc:
        print("RESOLVE ALERT ERROR:", exc)
        return jsonify(success=False, message="Could not resolve alert."), 500


@app.get("/admin")
@login_required("Admin")
def admin_dashboard(user):
    return render_template("admin.html", user=user)


@app.get("/api/admin/users")
@login_required("Admin")
def admin_users(user):
    try:
        users = [
            {
                "id": str(item.get("_id")),
                "name": item.get("name", ""),
                "email": item.get("email", ""),
                "phone": item.get("phone", ""),
                "role": item.get("role", ""),
            }
            for item in get_all_users()
        ]
        return jsonify(success=True, users=users)
    except Exception as exc:
        print("ADMIN USERS ERROR:", exc)
        return jsonify(success=False, message="Could not load users."), 500


@app.delete("/api/admin/users/<user_id>")
@login_required("Admin")
def admin_delete_user(user, user_id):
    if str(user_id) == str(user.get("_id")):
        return jsonify(success=False, message="You cannot delete your own account."), 400
    if delete_user(user_id):
        return jsonify(success=True, message="User deleted.")
    return jsonify(success=False, message="User not found."), 404


@app.get("/api/admin/alerts")
@login_required("Admin")
def admin_alerts(user):
    return jsonify(success=True, alerts=[serialize_doc(x) for x in get_all_alerts()])


@app.get("/api/admin/history")
@login_required("Admin")
def admin_history(user):
    return jsonify(success=True, history=[serialize_doc(x) for x in get_history()])


@app.get("/api/admin/status")
@login_required("Admin")
def admin_status(user):
    alerts = get_all_alerts()
    users = get_all_users()
    history = get_history()
    pending = sum(1 for x in alerts if x.get("status") == "Pending")
    resolved = sum(1 for x in alerts if x.get("status") == "Resolved")
    return jsonify(
        success=True,
        users=len(users),
        alerts=len(alerts),
        pending=pending,
        resolved=resolved,
        history=len(history),
    )


def serialize_doc(doc):
    result = {}
    for key, value in doc.items():
        if key == "_id" or isinstance(value, ObjectId):
            result[key] = str(value)
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify(success=False, message="Endpoint not found."), 404
    return render_template("login.html"), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    print("==========================================")
    print("       SAFE CAMPUS WEB APPLICATION")
    print("==========================================")
    print(f"Open: http://127.0.0.1:{port}")
    print("==========================================")
    app.run(host="0.0.0.0", port=port, debug=debug)
