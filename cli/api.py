import json
from pathlib import Path

import requests
from requests import RequestException


BASE_URL = "http://127.0.0.1:8000/api"
TOKEN_FILE = Path(".token_cache")
DEFAULT_TIMEOUT = 10

class ApiService:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = self.load_token()

    def load_token(self):
        if TOKEN_FILE.exists():
            try:
                data = json.loads(TOKEN_FILE.read_text())
                return data.get("access")
            except (json.JSONDecodeError, OSError):
                return None
        return None

    def save_token(self, tokens):
        TOKEN_FILE.write_text(json.dumps(tokens), encoding="utf-8")
        self.access_token = tokens.get("access")

    def _request(self, method, endpoint, **kwargs):
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
        if 'headers' not in kwargs:
            kwargs['headers'] = self._get_headers()
        try:
            response = self.session.request(method, f"{BASE_URL}/{endpoint}", **kwargs)
            return response, None
        except RequestException as exc:
            return None, str(exc)

    def login(self, username, password):
        response, error = self._request("post", "token/", data={"username": username, "password": password}, headers={})
        if error:
            return False, error
        if response.status_code == 200:
            self.save_token(response.json())
            return True, "Login successful"
        return False, "Invalid credentials"

    def register(self, data):
        response, error = self._request("post", "register/", json=data, headers={})
        if error:
            return False, error
        if response.status_code == 201:
            resp_json = response.json()
            if "tokens" in resp_json:
                self.save_token(resp_json["tokens"])
            return True, "Registration successful"
        return False, f"Registration failed: {response.text}"

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}

    def get_restaurants(self):
        response, error = self._request("get", "restaurants/")
        if error or response.status_code != 200:
            return []
        return response.json()

    def get_my_profile(self):
        response, error = self._request("get", "profile/me/")
        if error or response.status_code != 200:
            return None
        return response.json()

    def create_order(self, items):
        # items is {id: quantity}
        response, error = self._request("post", "orders/", json={"items": items})
        if error:
            return {"error": error}, 0
        return response.json(), response.status_code

    def get_orders(self):
        response, error = self._request("get", "orders/")
        if error or response.status_code != 200:
            return []
        return response.json()

    def cancel_order(self, order_id):
        response, error = self._request("post", f"orders/{order_id}/cancel/")
        return bool(response and not error and response.status_code == 200)

    # Driver Methods
    def get_available_jobs(self):
        response, error = self._request("get", "orders/available_jobs/")
        if error or response.status_code != 200:
            return []
        return response.json()

    def accept_job(self, order_id):
        response, error = self._request("post", f"orders/{order_id}/accept_job/")
        return bool(response and not error and response.status_code == 200)

    def complete_job(self, order_id):
        response, error = self._request("post", f"orders/{order_id}/complete_job/")
        return bool(response and not error and response.status_code == 200)
    
    # OTP Methods
    def send_otp(self, email):
        """Send OTP to email"""
        response, error = self._request("post", "send-otp/", json={"email": email}, headers={})
        if error:
            return False, error
        if response.status_code == 200:
            return True, response.json().get("message", "OTP sent")
        return False, response.json().get("error", "Failed to send OTP")
    
    def verify_otp(self, email, otp_code):
        """Verify OTP code"""
        response, error = self._request("post", "verify-otp/", json={"email": email, "otp": otp_code}, headers={})
        if error:
            return False, error
        data = response.json()
        if response.status_code == 200 and data.get("verified"):
            return True, data.get("message", "Verified")
        return False, data.get("message", "Invalid OTP")

