import flet as ft


PRIMARY = "#0F8B83"
DARK = "#06132A"
BG = "#F4F6FA"


def create_register_view(page, auth_service):
    username = ft.TextField(
        label="Username",
        prefix_icon=ft.Icons.PERSON,
        border_radius=12,
        autofill_hints=[ft.AutofillHint.USERNAME],
    )

    email = ft.TextField(
        label="Email",
        prefix_icon=ft.Icons.EMAIL,
        border_radius=12,
        autofill_hints=[ft.AutofillHint.EMAIL],
    )

    first_name = ft.TextField(  
        label="First Name",
        prefix_icon=ft.Icons.BADGE,
        border_radius=12,
    )

    last_name = ft.TextField(  
        label="Last Name",
        prefix_icon=ft.Icons.BADGE,
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

    def validate_email(email_value):
        """Basic email validation"""
        return "@" in email_value and "." in email_value.split("@")[-1]

    def register_click(e):
        # Clear previous message
        message_text.value = ""
        message_text.color = ft.Colors.RED
        page.update()

        # Validation
        if not username.value:
            message_text.value = "Username is required."
            page.update()
            return

        if not email.value or not validate_email(email.value):
            message_text.value = "Please enter a valid email address."
            page.update()
            return

        if not first_name.value:
            message_text.value = "First name is required."
            page.update()
            return

        if not last_name.value:
            message_text.value = "Last name is required."
            page.update()
            return

        if not password.value:
            message_text.value = "Password is required."
            page.update()
            return

        if password.value != confirm_password.value:
            message_text.value = "Passwords do not match."
            page.update()
            return

        if len(password.value) < 6:
            message_text.value = "Password must be at least 6 characters."
            page.update()
            return

        # Show loading state
        message_text.value = "Creating account..."
        message_text.color = ft.Colors.BLUE
        page.update()

        result = auth_service.register(
            username=username.value,
            email=email.value,
            password=password.value,
            confirm_password=confirm_password.value,
            first_name=first_name.value,  # Add first_name
            last_name=last_name.value,    # Add last_name
            member_type="student"          # Default member type
        )

        # Check for success
        if result.get("token") and result.get("user"):
            # Registration successful and user is auto-logged in
            message_text.value = "Account created successfully! Redirecting..."
            message_text.color = ft.Colors.GREEN
            page.update()
            
            # Small delay to show success message then navigate
            page.go_to("/home")
            
        elif result.get("error"):
            message_text.value = result.get("error", "Registration failed. Please try again.")
            message_text.color = ft.Colors.RED
            page.update()
        else:
            message_text.value = "Registration failed. Please try again."
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
            actions=[
                ft.ElevatedButton(
                    "Configure Server",
                    icon=ft.Icons.SETTINGS,
                    bgcolor=ft.Colors.GREY_200,
                    color=DARK,
                    width=360,
                    on_click=lambda e: page.go_to("/settings"),
                ),
            ],
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
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(expand=True, content=first_name),
                                            ft.Container(expand=True, content=last_name),
                                        ],
                                    ),
                                    password,
                                    confirm_password,
                                    ft.Container(height=5),
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