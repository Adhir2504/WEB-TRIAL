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


def category_button(title, selected, on_click):
    return ft.ElevatedButton(
        title,
        bgcolor=PRIMARY if selected else ft.Colors.WHITE,
        color=ft.Colors.WHITE if selected else DARK,
        on_click=on_click,
    )


def create_facility_card(page, facility):
    facility_id = facility.get("facility_id")

    return ft.Card(
        elevation=3,
        content=ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=18,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=130,
                        bgcolor=ft.Colors.BLUE_GREY_300,
                        border_radius=ft.border_radius.only(top_left=18, top_right=18),
                        padding=10,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Container(
                                    content=ft.Text("Available", color=ft.Colors.WHITE, size=11),
                                    bgcolor=ft.Colors.GREEN,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=20,
                                )
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    facility.get("facility_name", "Facility").upper(),
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=DARK,
                                ),
                                ft.Text(
                                    f"{facility.get('location', 'Gymnasium Complex')} • "
                                    f"{facility.get('courts_count', 0)} court(s)",
                                    size=13,
                                    color=ft.Colors.BLUE_GREY,
                                ),
                                ft.Text(
                                    f"Category: {facility.get('facility_type', 'N/A')}",
                                    size=13,
                                    color=PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    facility.get(
                                        "description",
                                        "Reserve this facility and choose an available court and time slot.",
                                    ),
                                    size=14,
                                    color=DARK,
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.OutlinedButton(
                                            "View Details",
                                            expand=True,
                                            on_click=lambda e, fid=facility_id: page.go_to(
                                                f"/facility/{fid}"
                                            ),
                                        ),
                                        ft.ElevatedButton(
                                            "Book Now",
                                            expand=True,
                                            bgcolor=PRIMARY,
                                            color=ft.Colors.WHITE,
                                            on_click=lambda e, fid=facility_id: page.go_to(
                                                f"/facility/{fid}"
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )


def create_facilities_view(page, api_service, auth_service):
    facilities_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=14,
    )

    all_facilities = []
    selected_category = {"value": "All"}

    categories = ["All", "Football", "Volleyball", "Badminton"]

    category_row = ft.Row(
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        controls=[],
    )

    def set_category(category):
        selected_category["value"] = category
        render_facilities()

    def refresh_category_buttons():
        category_row.controls.clear()

        for category in categories:
            category_row.controls.append(
                category_button(
                    category,
                    selected_category["value"] == category,
                    lambda e, c=category: set_category(c),
                )
            )

    def render_facilities():
        facilities_column.controls.clear()
        refresh_category_buttons()

        current_category = selected_category["value"].lower()

        filtered_facilities = []

        for facility in all_facilities:
            facility_type = (facility.get("facility_type") or "").lower()
            facility_name = (facility.get("facility_name") or "").lower()

            if current_category == "all":
                filtered_facilities.append(facility)
            elif current_category in facility_type or current_category in facility_name:
                filtered_facilities.append(facility)

        if not filtered_facilities:
            facilities_column.controls.append(
                ft.Container(
                    padding=20,
                    border_radius=18,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Text(
                        "No facilities found for this category.",
                        color=ft.Colors.BLUE_GREY,
                    ),
                )
            )
            page.update()
            return

        for facility in filtered_facilities:
            facilities_column.controls.append(create_facility_card(page, facility))

        page.update()

    def load_facilities():
        facilities_column.controls.clear()
        facilities_column.controls.append(ft.Text("Loading facilities..."))
        page.update()

        try:
            response = api_service.get_facilities()

            if not response.ok:
                facilities_column.controls.clear()
                facilities_column.controls.append(
                    ft.Text("Could not load facilities.", color=ft.Colors.RED)
                )
                page.update()
                return

            all_facilities.clear()
            all_facilities.extend(response.json())

            render_facilities()

        except Exception as ex:
            facilities_column.controls.clear()
            facilities_column.controls.append(
                ft.Text(f"Error: {ex}", color=ft.Colors.RED)
            )
            page.update()

    refresh_category_buttons()
    load_facilities()

    return ft.View(
        route="/facilities",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("Facilities", color=DARK, weight=ft.FontWeight.BOLD),
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
                    spacing=16,
                    controls=[
                        ft.Text(
                            "Book University Facilities",
                            size=25,
                            weight=ft.FontWeight.BOLD,
                            color=DARK,
                        ),
                        ft.Text(
                            "Choose a category and reserve available courts across campus.",
                            size=14,
                            color=ft.Colors.BLUE_GREY,
                        ),
                        ft.Container(
                            padding=14,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=18,
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Text(
                                        "Categories",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    category_row,
                                ],
                            ),
                        ),
                        facilities_column,
                    ],
                ),
            )
        ],
        navigation_bar=create_bottom_nav(page, 1),
    )