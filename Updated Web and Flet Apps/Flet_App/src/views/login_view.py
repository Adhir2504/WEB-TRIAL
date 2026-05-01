import flet as ft

PRIMARY = "#0F8B83"
DARK = "#06132A"
BG = "#F4F6FA"


def create_login_view(page, auth_service):
    email = ft.TextField(
        label="Email",
        prefix_icon=ft.Icons.EMAIL,
        border_radius=12,
    )

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        border_radius=12,
    )

    error_text = ft.Text("", color=ft.Colors.RED)

    def login_click(e):
        if not email.value or not password.value:
            error_text.value = "Please enter email and password."
            page.update()
            return

        # Show loading indicator
        error_text.value = "Logging in..."
        error_text.color = ft.Colors.BLUE
        page.update()

        result = auth_service.login(email.value, password.value)

        if result.get("token"):
            error_text.value = ""
            page.update()
            page.go_to("/home")
        else:
            error_text.value = result.get("error", "Login failed.")
            error_text.color = ft.Colors.RED
            page.update()

    return ft.View(
        route="/login",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("UniBook", color=DARK, weight=ft.FontWeight.BOLD),
            center_title=True,
            elevation=0,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_size=22,
                    tooltip="Server Settings",
                    on_click=lambda e: page.go_to("/settings"),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.TRANSPARENT,
                        overlay_color=ft.Colors.TRANSPARENT,
                    ),
                ),
            ],
        ),
        controls=[
            ft.Container(
                expand=True,
                padding=22,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=24,
                            border_radius=24,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                width=360,
                                spacing=18,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                width=38,
                                                height=38,
                                                bgcolor=DARK,
                                                border_radius=9,
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Text(
                                                    "U",
                                                    color=ft.Colors.WHITE,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ),
                                            ft.Text(
                                                "UniBook",
                                                size=22,
                                                weight=ft.FontWeight.BOLD,
                                                color=DARK,
                                            ),
                                        ],
                                    ),
                                    ft.Text(
                                        "Sign In",
                                        size=30,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    ft.Text(
                                        "Welcome back! Please sign in to your account.",
                                        size=14,
                                        color=ft.Colors.BLUE_GREY,
                                    ),
                                    email,
                                    password,
                                    error_text,
                                    ft.ElevatedButton(
                                        "Sign In",
                                        bgcolor=PRIMARY,
                                        color=ft.Colors.WHITE,
                                        width=360,
                                        on_click=login_click,
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text(
                                                "Don't have an account?",
                                                color=ft.Colors.BLUE_GREY,
                                            ),
                                            ft.TextButton(
                                                "Sign up here",
                                                on_click=lambda e: page.go_to("/register"),
                                            ),
                                        ],
                                    ),
                                    
                                    # Add a simple divider before settings button
                                    ft.Container(
                                        height=10,
                                    ),
                                    
                                    # Beautiful centered settings button
                                    ft.OutlinedButton(
                                        content=ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Icon(ft.Icons.SETTINGS, size=16, color=ft.Colors.GREY_600),
                                                ft.Text(
                                                    "Server Settings",
                                                    size=13,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                        ),
                                        style=ft.ButtonStyle(
                                            side=ft.BorderSide(color=ft.Colors.GREY_300, width=1),
                                            shape=ft.RoundedRectangleBorder(radius=30),
                                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                        ),
                                        on_click=lambda e: page.go_to("/settings"),
                                    ),
                                ],
                            ),
                        )
                    ],
                ),
            )
        ],
    )