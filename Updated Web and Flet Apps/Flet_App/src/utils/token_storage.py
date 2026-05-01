class TokenStorage:
    _token = None
    _user = None  # Add this to store user data

    @classmethod
    def save_token(cls, token):
        cls._token = token

    @classmethod
    def get_token(cls):
        return cls._token

    @classmethod
    def clear_token(cls):
        cls._token = None
        cls._user = None  # Also clear user data on logout

    @classmethod
    def save_user(cls, user):
        """Save user information"""
        cls._user = user

    @classmethod
    def get_user(cls):
        """Get stored user information"""
        return cls._user

    @classmethod
    def is_authenticated(cls):
        """Check if user is logged in"""
        return cls._token is not None