let idleSeconds = 0;
let warned = false;

const IDLE_LIMIT = 300;
const WARNING_TIME = 270;

function resetIdle() {
    idleSeconds = 0;
    warned = false;
}

setInterval(() => {
    idleSeconds++;

    if (idleSeconds === WARNING_TIME && !warned) {
        warned = true;

        const stay = confirm(
            "Your session will expire in 30 seconds due to inactivity.\n\nClick OK to stay logged in."
        );

        if (stay) {
            fetch("/accounts/ping/", { method: "POST" });
            resetIdle();
        }
    }

    if (idleSeconds >= IDLE_LIMIT) {
        window.location.href = "/accounts/logout/";
    }
}, 1000);

["mousemove", "keydown", "click", "scroll"].forEach(evt => {
    document.addEventListener(evt, resetIdle, true);
});

