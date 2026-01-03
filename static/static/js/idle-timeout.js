(() => {
    const IDLE_LIMIT = 270000;   // 4 min 30 sec
    const LOGOUT_TIME = 300000;  // 5 min

    let idleTimer, logoutTimer;

    function resetTimers() {
        clearTimeout(idleTimer);
        clearTimeout(logoutTimer);

        idleTimer = setTimeout(showWarning, IDLE_LIMIT);
        logoutTimer = setTimeout(forceLogout, LOGOUT_TIME);
    }

    function showWarning() {
        const stay = confirm(
            "You have been inactive.\n\n" +
            "Your session will expire in 30 seconds.\n\n" +
            "Click OK to continue."
        );

        if (stay) {
            fetch("/accounts/ping/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            }).then(resetTimers);
        }
    }

    function forceLogout() {
        window.location.href = "/accounts/logout/";
    }

    function getCSRFToken() {
        return document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }

    ["mousemove", "keydown", "click", "scroll"].forEach(evt =>
        document.addEventListener(evt, resetTimers)
    );

    resetTimers();
})();
