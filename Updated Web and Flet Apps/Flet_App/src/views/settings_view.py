import flet as ft
from config import server_config

PRIMARY = "#0F8B83"
DARK = "#06132A"
BG = "#F4F6FA"

def create_settings_view(page, auth_service, api_service):
    """Settings screen where users can configure the server IP"""
    
    # Only set storage if available
    if hasattr(page, 'client_storage'):
        server_config.set_storage(page.client_storage)
    
    # Get current IP
    current_ip = server_config.get_ip()
    
    # Create IP input field
    ip_field = ft.TextField(
        label="Server IP Address",
        hint_text="e.g., 192.168.1.100 or your-computer-name.local",
        value=current_ip,
        width=400,
        prefix_icon=ft.Icons.DNS,
        border_radius=12,
    )
    
    port_field = ft.TextField(
        label="Port",
        hint_text="8000",
        value=str(server_config.DEFAULT_PORT),
        width=150,
        prefix_icon=ft.Icons.CABLE,
        border_radius=12,
    )
    
    status_text = ft.Text("", size=12)
    
    def test_connection(e):
        """Test if the server is reachable"""
        import requests
        
        ip = ip_field.value.strip()
        port = port_field.value.strip()
        test_url = f"http://{ip}:{port}/api/auth/login/"
        
        status_text.value = "Testing connection..."
        status_text.color = ft.Colors.BLUE
        page.update()
        
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code in [200, 400, 405]:
                status_text.value = "✓ Connection successful! Server is reachable."
                status_text.color = ft.Colors.GREEN
            else:
                status_text.value = f"✗ Server responded with status: {response.status_code}"
                status_text.color = ft.Colors.ORANGE
        except requests.ConnectionError:
            status_text.value = "✗ Cannot connect. Make sure Django is running on your PC."
            status_text.color = ft.Colors.RED
        except Exception as ex:
            status_text.value = f"✗ Error: {str(ex)[:80]}"
            status_text.color = ft.Colors.RED
        
        page.update()
    
    def save_and_restart(e):
        """Save settings and return to home"""
        ip = ip_field.value.strip()
        port = port_field.value.strip()
        
        if not ip:
            status_text.value = "Please enter an IP address"
            status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Save the IP
        server_config.set_ip(ip)
        
        status_text.value = f"Settings saved! Server set to: {ip}:{port}"
        status_text.color = ft.Colors.GREEN
        page.update()
        
        # Go back to home after a moment
        page.go_to("/login")
    
    def detect_auto(e):
        """Auto-detect the server IP"""
        auto_ip = server_config.get_local_ip()
        ip_field.value = auto_ip
        status_text.value = f"Auto-detected IP: {auto_ip}"
        status_text.color = ft.Colors.BLUE
        page.update()
    
    def show_help(e):
        """Show help dialog"""
        page.dialog = ft.AlertDialog(
            title=ft.Text("How to find your server IP", size=20),
            content=ft.Column([
                ft.Text("On Windows (the computer running Django):", weight=ft.FontWeight.BOLD),
                ft.Text("1. Open Command Prompt", size=12),
                ft.Text("2. Type: ipconfig", size=12),
                ft.Text("3. Look for 'IPv4 Address' (usually 192.168.x.x)", size=12),
                ft.Divider(),
                ft.Text("On Mac/Linux:", weight=ft.FontWeight.BOLD),
                ft.Text("1. Open Terminal", size=12),
                ft.Text("2. Type: ifconfig", size=12),
                ft.Text("3. Look for 'inet' (usually 192.168.x.x)", size=12),
                ft.Divider(),
                ft.Text("Make sure Django is running on your PC:", weight=ft.FontWeight.BOLD),
                ft.Text("python manage.py runserver 0.0.0.0:8000", size=11, selectable=True),
                ft.Text("Your phone must be on the same WiFi network!", size=11, color=ft.Colors.ORANGE),
            ], spacing=10),
            actions=[ft.TextButton("Close", on_click=lambda e: page.close_dialog())],
        )
        page.dialog.open = True
        page.update()
    
    return ft.View(
        route="/settings",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("Server Settings", color=DARK, weight=ft.FontWeight.BOLD),
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
                                width=400,
                                spacing=20,
                                controls=[
                                    ft.Icon(ft.Icons.SETTINGS, size=40, color=PRIMARY),
                                    ft.Text(
                                        "Server Configuration",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    ft.Text(
                                        "Enter the IP address of the computer running the Django server",
                                        size=14,
                                        color=ft.Colors.GREY,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Divider(),
                                    ip_field,
                                    ft.Row([
                                        port_field,
                                        ft.IconButton(
                                            icon=ft.Icons.MY_LOCATION,
                                            tooltip="Auto-detect IP",
                                            on_click=detect_auto,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.HELP,
                                            tooltip="How to find IP",
                                            on_click=show_help,
                                        ),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.ResponsiveRow(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                col={"xs": 12, "sm": 6, "md": 6},
                                                content=ft.OutlinedButton(
                                                    "Test Connection",
                                                    icon=ft.Icons.NETWORK_CHECK,
                                                    on_click=test_connection,
                                                    width=float('inf'),  # Full width of container
                                                ),
                                            ),
                                            ft.Container(
                                                col={"xs": 12, "sm": 6, "md": 6},
                                                content=ft.ElevatedButton(
                                                    "Save & Continue",
                                                    icon=ft.Icons.SAVE,
                                                    bgcolor=PRIMARY,
                                                    color=ft.Colors.WHITE,
                                                    on_click=save_and_restart,
                                                    width=float('inf'),  # Full width of container
                                                ),
                                            ),
                                        ],
                                    ),
                                    status_text,
                                    ft.Text(
                                        "⚠️ Make sure Django is running on your PC:",
                                        size=11,
                                        color=ft.Colors.ORANGE,
                                    ),
                                    ft.Text(
                                        "(python manage.py runserver 0.0.0.0:8000)",
                                        size=10,
                                        selectable=True,
                                    ),
                                ],
                            ),
                        )
                    ],
                ),
            )
        ],
    )