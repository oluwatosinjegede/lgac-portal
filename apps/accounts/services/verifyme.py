import requests
from django.conf import settings


class VerifyMeService:
    """
    Handles all VerifyMe NIN verification logic.
    """

    @staticmethod
    def verify_nin(nin: str) -> dict:
        """
        Verifies a Nigerian NIN via VerifyMe.
        Returns: { "verified": bool, "data": dict | None }
        """

        url = f"{settings.VERIFYME_BASE_URL}/v1/verifications/nin"

        headers = {
            "Authorization": f"Bearer {settings.VERIFYME_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "nin": nin
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=int(settings.VERIFYME_TIMEOUT),
            )

            if response.status_code != 200:
                return {"verified": False, "data": None}

            result = response.json()

            # VerifyMe convention (safe assumption)
            if result.get("status") is True:
                return {
                    "verified": True,
                    "data": result.get("data"),
                }

            return {"verified": False, "data": None}

        except requests.RequestException:
            return {"verified": False, "data": None}

