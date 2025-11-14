from django.conf import settings
from django.contrib.auth import logout
import datetime

class AutoLogout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 🚫 Skip API paths (public APIs must NOT use AutoLogout)
        if request.path.startswith("/api/"):
            return self.get_response(request)

        # 🚫 Skip static or media paths
        if request.path.startswith("/static/") or request.path.startswith("/media/"):
            return self.get_response(request)

        # If user is not logged in, skip
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Existing logic
        current_datetime = datetime.datetime.now()
        last_activity = request.session.get("last_activity")

        if last_activity:
            elapsed_time = (current_datetime - datetime.datetime.fromisoformat(last_activity)).seconds
            if elapsed_time > settings.SESSION_COOKIE_AGE:
                logout(request)
                request.session.flush()

        request.session["last_activity"] = current_datetime.isoformat()

        return self.get_response(request)
