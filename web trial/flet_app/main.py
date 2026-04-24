import flet as ft

from views.login_view import create_login_view
from views.home_view import create_home_view
from views.facilities_view import create_facilities_view
from views.facility_detail_view import create_facility_detail_view
from views.booking_view import create_bookings_view
from views.profile_view import create_profile_view
from views.register_view import create_register_view
from services.auth_service import AuthService
from services.api_service import ApiService
from utils.token_storage import TokenStorage


def main(page: ft.Page):
    page.title = "UniBook Mobile"
    page.window.width = 430
    page.window.height = 780
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    auth_service = AuthService()
    api_service = ApiService()

    def go(route):
        page.go(route)

    page.go_to = go

    def route_change(e):
        page.views.clear()

        if page.route == "/login":
            page.views.append(create_login_view(page, auth_service))

        elif page.route == "/register":
            page.views.append(create_register_view(page, auth_service))

        elif page.route == "/home":
            page.views.append(create_home_view(page, api_service))

        elif page.route == "/facilities":
            page.views.append(create_facilities_view(page, api_service, auth_service))

        elif page.route.startswith("/facility/"):
            facility_id = page.route.split("/")[-1]
            page.views.append(create_facility_detail_view(page, api_service, facility_id))

        elif page.route == "/bookings":
            page.views.append(create_bookings_view(page, api_service))

        elif page.route == "/profile":
            page.views.append(create_profile_view(page, auth_service))

        else:
            page.views.append(create_login_view(page, auth_service))

        page.update()

    page.on_route_change = route_change

    if TokenStorage.get_token():
        page.go_to("/home")
    else:
        page.go_to("/login")


ft.run(main)