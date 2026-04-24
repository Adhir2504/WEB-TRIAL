import requests
from utils.token_storage import TokenStorage


class AuthService:
    BASE_URL = "http://127.0.0.1:8000"

    def login(self, email: str, password: str):
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/login/",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.ok:
                data = response.json()
                token = data.get("token")

                if token:
                    TokenStorage.save_token(token)

                return data

            return {"error": response.text}

        except requests.RequestException as exc:
            return {"error": str(exc)}

    def get_token(self):
        return TokenStorage.get_token()

    def logout(self):
        TokenStorage.clear_token()

    def register(self, username: str, email: str, password: str, confirm_password: str):
        if password != confirm_password:
            return {"error": "Passwords do not match."}

        try:
            response = requests.post(
                f"{self.BASE_URL}/api/register/",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.ok:
                return response.json()

            return {"error": response.text}

        except requests.RequestException as exc:
            return {"error": str(exc)}