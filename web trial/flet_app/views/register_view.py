import flet as ft


PRIMARY = "#0F8B83"
DARK = "#06132A"
BG = "#F4F6FA"


def create_register_view(page, auth_service):
    username = ft.TextField(
        label="Username",
        prefix_icon=ft.Icons.PERSON,
        border_radius=12,
    )

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

    confirm_password = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        border_radius=12,
    )

    message_text = ft.Text("", color=ft.Colors.RED)

    def register_click(e):
        if not username.value or not email.value or not password.value or not confirm_password.value:
            message_text.value = "Please fill in all fields."
            message_text.color = ft.Colors.RED
            page.update()
            return

        result = auth_service.register(
            username.value,
            email.value,
            password.value,
            confirm_password.value,
        )

        if result.get("token") or result.get("success") or result.get("user"):
            message_text.value = "Account created successfully. Please sign in."
            message_text.color = ft.Colors.GREEN
            page.update()
            page.go_to("/login")
        else:
            message_text.value = result.get("error", "Registration failed.")
            message_text.color = ft.Colors.RED
            page.update()

    return ft.View(
        route="/register",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("Create Account", color=DARK, weight=ft.FontWeight.BOLD),
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: page.go_to("/login"),
            ),
        ),
        controls=[
            ft.Container(
                expand=True,
                padding=22,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=24,
                            border_radius=24,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                width=360,
                                spacing=16,
                                controls=[
                                    ft.Text(
                                        "Sign Up",
                                        size=30,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    ft.Text(
                                        "Create your UniBook account to start booking facilities.",
                                        size=14,
                                        color=ft.Colors.BLUE_GREY,
                                    ),
                                    username,
                                    email,
                                    password,
                                    confirm_password,
                                    message_text,
                                    ft.ElevatedButton(
                                        "Create Account",
                                        bgcolor=PRIMARY,
                                        color=ft.Colors.WHITE,
                                        width=360,
                                        on_click=register_click,
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text(
                                                "Already have an account?",
                                                color=ft.Colors.BLUE_GREY,
                                            ),
                                            ft.TextButton(
                                                "Sign in",
                                                on_click=lambda e: page.go_to("/login"),
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