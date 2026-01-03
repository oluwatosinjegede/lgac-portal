import time
from django.contrib.auth import logout
from django.shortcuts import redirect

class IdleTimeoutMiddleware:
    """
    Logs out users after inactivity.
    Excludes Django admin and static/media paths.
    """

    EXEMPT_PATHS = (
        "/admin/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ? Skip admin and static/media
        if path.startswith(self.EXEMPT_PATHS):
            return self.get_response(request)

        if request.user.is_authenticated:
            now = time.time()
            last_activity = request.session.get("last_activity")

            if last_activity and now - last_activity > 300:
                logout(request)
                request.session.flush()
                return redirect("/accounts/login/?expired=1")

            request.session["last_activity"] = now

        return self.get_response(request)
