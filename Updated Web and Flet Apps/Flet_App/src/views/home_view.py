import flet as ft


PRIMARY = "#0F8B83"
DARK = "#06132A"
BG = "#F4F6FA"


def nav_bar(page, selected_index=0):
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


def quick_icon(page, icon, title, route):
    return ft.Container(
        expand=True,
        padding=14,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        on_click=lambda e: page.go_to(route),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Container(
                    width=46,
                    height=46,
                    border_radius=14,
                    bgcolor="#E6F4F3",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icon, color=PRIMARY, size=28),
                ),
                ft.Text(
                    title,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=DARK,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )


def popular_card(page, facility, popular=False):
    badge_text = "Most Popular" if popular else "Available"
    badge_color = ft.Colors.ORANGE if popular else ft.Colors.GREEN
    facility_id = facility.get("facility_id")

    return ft.Card(
        elevation=2,
        content=ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=105,
                        bgcolor=ft.Colors.BLUE_GREY_300,
                        border_radius=ft.border_radius.only(top_left=16, top_right=16),
                        padding=10,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        badge_text,
                                        color=ft.Colors.WHITE,
                                        size=10,
                                    ),
                                    bgcolor=badge_color,
                                    padding=ft.padding.symmetric(horizontal=9, vertical=4),
                                    border_radius=20,
                                )
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=14,
                        content=ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text(
                                    facility.get("facility_name", "Facility").upper(),
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=DARK,
                                ),
                                ft.Text(
                                    f"{facility.get('location', 'Campus')} • {facility.get('facility_type', 'Sports')}",
                                    size=12,
                                    color=ft.Colors.BLUE_GREY,
                                ),
                                ft.Text(
                                    f"{facility.get('bookings_count', 0)} booking(s) this week",
                                    size=12,
                                    color=PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.ElevatedButton(
                                    "Book Now",
                                    bgcolor=PRIMARY,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda e, fid=facility_id: page.go_to(f"/facility/{fid}"),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )


def create_home_view(page, api_service):
    top_facilities_column = ft.Column(spacing=12)

    def load_top_facilities():
        top_facilities_column.controls.clear()

        try:
            response = api_service.get_top_facilities()

            if response.ok:
                facilities = response.json()

                if not facilities:
                    top_facilities_column.controls.append(
                        ft.Text("No popular facilities yet.", color=ft.Colors.BLUE_GREY)
                    )
                else:
                    for index, facility in enumerate(facilities):
                        top_facilities_column.controls.append(
                            popular_card(page, facility, popular=(index == 0))
                        )
            else:
                top_facilities_column.controls.append(
                    ft.Text("Could not load top facilities.", color=ft.Colors.RED)
                )

        except Exception as ex:
            top_facilities_column.controls.append(
                ft.Text(f"Error: {ex}", color=ft.Colors.RED)
            )

    load_top_facilities()
    return ft.View(
        route="/home",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            automatically_imply_leading=False,
            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        bgcolor=DARK,
                        border_radius=8,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "U",
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                    ft.Text(
                        "UniBook",
                        weight=ft.FontWeight.BOLD,
                        color=DARK,
                    ),
                ],
            ),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.PERSON,
                    on_click=lambda e: page.go_to("/profile"),
                )
            ],
        ),
        controls=[
            ft.Container(
                expand=True,
                padding=16,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=18,
                    controls=[
                        ft.Container(
                            padding=22,
                            border_radius=24,
                            bgcolor=DARK,
                            content=ft.Column(
                                spacing=14,
                                controls=[
                                    ft.Text(
                                        "WELCOME TO UNIBOOK",
                                        color="#A7F3EF",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Reserve your campus courts instantly.",
                                        color=ft.Colors.WHITE,
                                        size=27,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Book football, volleyball, badminton and other facilities without waiting in line.",
                                        color=ft.Colors.WHITE70,
                                        size=14,
                                    ),
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.ElevatedButton(
                                                "Browse",
                                                bgcolor=PRIMARY,
                                                color=ft.Colors.WHITE,
                                                on_click=lambda e: page.go_to("/facilities"),
                                            ),
                                            ft.OutlinedButton(
                                                "My Bookings",
                                                on_click=lambda e: page.go_to("/bookings"),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),

                        ft.Text(
                            "Quick Actions",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=DARK,
                        ),

                        ft.Row(
                            spacing=12,
                            controls=[
                                quick_icon(
                                    page,
                                    ft.Icons.SPORTS_SOCCER,
                                    "Facilities",
                                    "/facilities",
                                ),
                                quick_icon(
                                    page,
                                    ft.Icons.EVENT_NOTE,
                                    "Bookings",
                                    "/bookings",
                                ),
                                quick_icon(
                                    page,
                                    ft.Icons.PERSON,
                                    "Profile",
                                    "/profile",
                                ),
                            ],
                        ),

                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Top 3 Most Booked This Week",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=DARK,
                                ),
                                ft.Text(
                                    "Popular facilities students are booking now.",
                                    size=13,
                                    color=ft.Colors.BLUE_GREY,
                                ),
                            ],
                        ),

                        top_facilities_column,
                    ],
                ),
            )
        ],
        navigation_bar=nav_bar(page, 0),
    )