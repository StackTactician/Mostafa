import requests
from pathlib import Path
import json

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN_FILE = Path(".token_cache")

class ApiService:
    def __init__(self):
        self.access_token = self.load_token()

    def load_token(self):
        if TOKEN_FILE.exists():
            try:
                data = json.loads(TOKEN_FILE.read_text())
                return data.get("access")
            except:
                pass
        return None

    def save_token(self, tokens):
        TOKEN_FILE.write_text(json.dumps(tokens))
        self.access_token = tokens.get("access")

    def login(self, username, password):
        try:
            response = requests.post(f"{BASE_URL}/token/", data={"username": username, "password": password})
            if response.status_code == 200:
                self.save_token(response.json())
                return True, "Login successful"
            return False, "Invalid credentials"
        except Exception as e:
            return False, str(e)

    def register(self, data):
        try:
            response = requests.post(f"{BASE_URL}/register/", json=data)
            if response.status_code == 201:
                resp_json = response.json()
                if 'tokens' in resp_json:
                    self.save_token(resp_json['tokens'])
                return True, "Registration successful"
            return False, f"Registration failed: {response.text}"
        except Exception as e:
            return False, str(e)

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}

    def get_restaurants(self):
        response = requests.get(f"{BASE_URL}/restaurants/", headers=self._get_headers())
        return response.json() if response.status_code == 200 else []

    def get_my_profile(self):
        response = requests.get(f"{BASE_URL}/profile/me/", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        return None

    def create_order(self, items):
        # items is {id: quantity}
        response = requests.post(
            f"{BASE_URL}/orders/", 
            json={"items": items}, 
            headers=self._get_headers()
        )
        return response.json(), response.status_code

    def get_orders(self):
        response = requests.get(f"{BASE_URL}/orders/", headers=self._get_headers())
        return response.json() if response.status_code == 200 else []

    def cancel_order(self, order_id):
        response = requests.post(f"{BASE_URL}/orders/{order_id}/cancel/", headers=self._get_headers())
        return response.status_code == 200

    # Driver Methods
    def get_available_jobs(self):
        response = requests.get(f"{BASE_URL}/orders/available_jobs/", headers=self._get_headers())
        return response.json() if response.status_code == 200 else []

    def accept_job(self, order_id):
        response = requests.post(f"{BASE_URL}/orders/{order_id}/accept_job/", headers=self._get_headers())
        return response.status_code == 200

    def complete_job(self, order_id):
        response = requests.post(f"{BASE_URL}/orders/{order_id}/complete_job/", headers=self._get_headers())
        return response.status_code == 200
