import time
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class IdleTimeoutMiddleware:
    """
    Logs out ALL authenticated users after a period of inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.idle_timeout = getattr(settings, "IDLE_TIMEOUT", 300)

    def __call__(self, request):
        if request.user.is_authenticated:
            now = time.time()
            last_activity = request.session.get("last_activity", now)

            if now - last_activity > self.idle_timeout:
                logout(request)
                request.session.flush()
                return redirect("accounts:login")

            request.session["last_activity"] = now

        return self.get_response(request)

