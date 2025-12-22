## App: `apps/payments`

### `apps/payments/service.py`

import os
import requests
from django.conf import settings

PAYSTACK_SECRET = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE = 'https://api.paystack.co'


def initialize_payment(email, amount_kobo, reference, callback_url):
    url = f"{PAYSTACK_BASE}/transaction/initialize"
    headers = {'Authorization': f'Bearer {PAYSTACK_SECRET}'}
    data = {
        'email': email,
        'amount': amount_kobo,
        'reference': reference,
        'callback_url': callback_url,
    }
    resp = requests.post(url, json=data, headers=headers)
    return resp.json()


def verify_payment(reference):
    url = f"{PAYSTACK_BASE}/transaction/verify/{reference}"
    headers = {'Authorization': f'Bearer {PAYSTACK_SECRET}'}
    resp = requests.get(url, headers=headers)
    return resp.json()