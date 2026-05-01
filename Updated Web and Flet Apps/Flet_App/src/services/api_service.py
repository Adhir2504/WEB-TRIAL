import requests
from services.auth_service import AuthService
from config import server_config


class ApiService:
    def BASE_URL(self):
        return server_config.get_base_url()

    def __init__(self):
        self.auth_service = AuthService()

    def _headers(self):
        token = self.auth_service.get_token()

        headers = {
            "Content-Type": "application/json",
        }

        if token:
            headers["Authorization"] = f"Token {token}"

        return headers
    

    def get_top_facilities(self):
        return requests.get(
            f"{self.BASE_URL()}/api/mobile/top-facilities/",
            headers=self._headers(),
            timeout=10,
        )

    def get_facilities(self):
        return requests.get(
            f"{self.BASE_URL()}/api/mobile/facilities/",
            headers=self._headers(),
            timeout=10,
        )

    def get_facility_detail(self, facility_id):
        return requests.get(
            f"{self.BASE_URL()}/api/mobile/facilities/{facility_id}/",
            headers=self._headers(),
            timeout=10,
        )

    def get_slots(self, facility_id, selected_date):
        return requests.get(
            f"{self.BASE_URL()}/api/mobile/facilities/{facility_id}/slots/?date={selected_date}",
            headers=self._headers(),
            timeout=10,
        )

    def create_booking(self, payload):
        return requests.post(
            f"{self.BASE_URL()}/api/mobile/bookings/create/",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )

    def get_my_bookings(self):
        return requests.get(
            f"{self.BASE_URL()}/api/mobile/bookings/",
            headers=self._headers(),
            timeout=10,
        )

    def cancel_booking(self, booking_id):
        return requests.post(
            f"{self.BASE_URL()}/api/mobile/bookings/{booking_id}/cancel/",
            headers=self._headers(),
            timeout=10,
        )