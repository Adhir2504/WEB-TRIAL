import requests
from utils.token_storage import TokenStorage
from config import server_config

class AuthService:
    # Don't hardcode BASE_URL anymore - get it from config
    @property
    def BASE_URL(self):
        return server_config.get_base_url()
    
    def __init__(self):
        # Optional: You can still access the URL directly
        pass
    
    def get_token(self):
        return TokenStorage.get_token()
    
    def login(self, email: str, password: str):
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/auth/login/",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            
            if response.ok:
                data = response.json()
                token = data.get("token")
                user = data.get("user")
                
                if token:
                    TokenStorage.save_token(token)
                if user:
                    TokenStorage.save_user(user)
                
                return data
            
            return {"error": response.text}
        
        except requests.RequestException as exc:
            return {"error": str(exc)}
    
    def register(self, username: str, email: str, password: str, confirm_password: str, first_name: str = "", last_name: str = "", member_type: str = "student"):
        if password != confirm_password:
            return {"error": "Passwords do not match."}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/auth/register/",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "member_type": member_type,
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            
            if response.ok:
                data = response.json()
                if data.get("token") and data.get("user"):
                    TokenStorage.save_token(data.get("token"))
                    TokenStorage.save_user(data.get("user"))
                return data
            
            return {"error": response.text}
        
        except requests.RequestException as exc:
            return {"error": str(exc)}
    
    def logout(self):
        TokenStorage.clear_token()

    def get_current_user(self):
        return TokenStorage.get_user()

    @property
    def current_user(self):
        return TokenStorage.get_user()