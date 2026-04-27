import flet as ft


PRIMARY = "#0F8B83"
DARK = "#06132A"
BG = "#F4F6FA"


def create_bottom_nav(page, selected_index):
    routes = ["/home", "/facilities", "/bookings", "/profile"]

    return ft.NavigationBar(
        selected_index=selected_index,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.SPORTS, label="Facilities"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK, label="Bookings"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
        ],
        on_change=lambda e: page.go_to(routes[e.control.selected_index]),
    )


def detail_row(icon, label, value):
    return ft.Container(
        padding=12,
        border_radius=12,
        bgcolor="#F7F8FA",
        content=ft.Row(
            spacing=12,
            controls=[
                ft.Icon(icon, color=PRIMARY, size=22),
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(label, size=12, color=ft.Colors.BLUE_GREY),
                        ft.Text(value, size=15, weight=ft.FontWeight.BOLD, color=DARK),
                    ],
                ),
            ],
        ),
    )


def create_profile_view(page, auth_service):
    def logout_click(e):
        auth_service.logout()
        page.go_to("/login")

    return ft.View(
        route="/profile",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("Profile", color=DARK, weight=ft.FontWeight.BOLD),
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: page.go_to("/home"),
            ),
        ),
        controls=[
            ft.Container(
                padding=16,
                expand=True,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=18,
                    controls=[
                        ft.Container(
                            padding=18,
                            border_radius=22,
                            bgcolor=DARK,
                            content=ft.Row(
                                spacing=16,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=70,
                                        height=70,
                                        border_radius=35,
                                        bgcolor=PRIMARY,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text(
                                            "U",
                                            size=30,
                                            color=ft.Colors.WHITE,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ),
                                    ft.Column(
                                        expand=True,
                                        spacing=6,
                                        controls=[
                                            ft.Text(
                                                "Logged in user",
                                                size=21,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE,
                                            ),
                                            ft.Text(
                                                "Student / Staff Account",
                                                size=13,
                                                color=ft.Colors.WHITE70,
                                            ),
                                            ft.Container(
                                                padding=ft.padding.symmetric(horizontal=12, vertical=5),
                                                border_radius=20,
                                                bgcolor="#D9FBEA",
                                                content=ft.Text(
                                                    "ACTIVE",
                                                    size=11,
                                                    color="#0F5132",
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),

                        ft.Container(
                            padding=18,
                            border_radius=20,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    ft.Text(
                                        "Account Details",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    detail_row(
                                        ft.Icons.PERSON,
                                        "Username",
                                        "Logged in user",
                                    ),
                                    detail_row(
                                        ft.Icons.EMAIL,
                                        "Email",
                                        "Available after profile API",
                                    ),
                                    detail_row(
                                        ft.Icons.BADGE,
                                        "Member Type",
                                        "Student / Staff",
                                    ),
                                    detail_row(
                                        ft.Icons.VERIFIED_USER,
                                        "Status",
                                        "Active",
                                    ),
                                ],
                            ),
                        ),

                        ft.Container(
                            padding=18,
                            border_radius=20,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    ft.Text(
                                        "Actions",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    ft.ElevatedButton(
                                        "Logout",
                                        bgcolor=ft.Colors.RED,
                                        color=ft.Colors.WHITE,
                                        icon=ft.Icons.LOGOUT,
                                        on_click=logout_click,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            )
        ],
        navigation_bar=create_bottom_nav(page, 3),
    )