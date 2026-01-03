document.addEventListener("DOMContentLoaded", function () {
    const verifyBtn = document.getElementById("verifyNinBtn");
    const ninInput = document.getElementById("id_nin");
    const statusText = document.getElementById("ninStatus");
    const submitBtn = document.getElementById("submitBtn");

    if (!verifyBtn) {
        console.error("Verify NIN button not found");
        return;
    }

    verifyBtn.addEventListener("click", function () {
        const nin = ninInput.value.trim();

        if (!/^\d{11}$/.test(nin)) {
            statusText.textContent = "Enter a valid 11-digit NIN.";
            statusText.className = "text-danger";
            return;
        }

        statusText.textContent = "Verifying NIN...";
        statusText.className = "text-warning";

        fetch("/accounts/verify-nin/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ nin: nin }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.verified) {
                    statusText.textContent = "NIN verified successfully.";
                    statusText.className = "text-success";
                    submitBtn.disabled = false;
                } else {
                    statusText.textContent = data.message || "Verification failed.";
                    statusText.className = "text-danger";
                    submitBtn.disabled = true;
                }
            })
            .catch(error => {
                console.error(error);
                statusText.textContent = "Verification error. Try again.";
                statusText.className = "text-danger";
            });
    });
});
