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

        result = auth_service.login(email.value, password.value)

        if result.get("token"):
            page.go_to("/home")
        else:
            error_text.value = result.get("error", "Login failed.")
            page.update()

    return ft.View(
        route="/login",
        bgcolor=BG,
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
                                ],
                            ),
                        )
                    ],
                ),
            )
        ],
    )