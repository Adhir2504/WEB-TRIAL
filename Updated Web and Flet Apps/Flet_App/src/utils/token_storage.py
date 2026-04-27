class TokenStorage:
    _token = None

    @classmethod
    def save_token(cls, token):
        cls._token = token

    @classmethod
    def get_token(cls):
        return cls._token

    @classmethod
    def clear_token(cls):
        cls._token = None