import flet as ft
from datetime import date


PRIMARY = "#0F8B83"
DARK = "#06132A"
BG = "#F4F6FA"


def show_snack(page, message, color):
    snack = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color,
    )

    if hasattr(page, "open"):
        page.open(snack)
    else:
        page.snack_bar = snack
        page.snack_bar.open = True

    page.update()


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


def create_facility_detail_view(page, api_service, facility_id):
    selected_date = None

    def date_changed(e):
        if e.control.value:
            picked_date = e.control.value.date()
            selected_date.value = picked_date.strftime("%Y-%m-%d")
        page.update()

    date_picker = ft.DatePicker(
        on_change=date_changed,
    )

    page.overlay.append(date_picker)

    def open_date_picker():
        date_picker.open = True
        page.update()

    selected_date = ft.TextField(
        label="Booking date",
        value=date.today().strftime("%Y-%m-%d"),
        hint_text="YYYY-MM-DD",
        prefix_icon=ft.Icons.CALENDAR_MONTH,
        read_only=True,
        on_click=lambda e: open_date_picker(),
    )

    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=16,
    )

    facility_data = {}
    slots_data = {}
    selected_court = {}

    def book_slot(court_id, start_time, end_time):
        payload = {
            "facility_id": facility_id,
            "court_id": court_id,
            "booking_date": selected_date.value,
            "start_time": start_time,
            "end_time": end_time,
            "notes": "",
        }

        response = api_service.create_booking(payload)

        if response.ok:
            show_snack(page, "Booking created successfully.", ft.Colors.GREEN)
            page.go_to("/bookings")
        else:
            try:
                error = response.json().get("error", "Booking failed.")
            except Exception:
                error = "Booking failed."

            show_snack(page, error, ft.Colors.RED)

    def show_info():
        content.controls.clear()

        courts = facility_data.get("courts", [])

        court_list = []
        if courts:
            for court in courts:
                court_list.append(
                    ft.Text(
                        f"• {court.get('court_name')} - {court.get('sport_type')} "
                        f"(Capacity: {court.get('capacity')})",
                        size=14,
                    )
                )
        else:
            court_list.append(
                ft.Text("No courts found for this facility.", color=ft.Colors.BLUE_GREY)
            )

        content.controls.extend(
            [
                ft.Container(
                    height=180,
                    border_radius=20,
                    bgcolor=ft.Colors.BLUE_GREY_300,
                ),

                ft.Container(
                    padding=18,
                    border_radius=20,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text(
                                facility_data.get("facility_name", "Facility"),
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=DARK,
                            ),
                            ft.Text(
                                f"📍 {facility_data.get('location', 'Gymnasium Complex')}",
                                size=14,
                                color=ft.Colors.BLUE_GREY,
                            ),
                            ft.Text(
                                f"🏷️ {facility_data.get('facility_type', 'Sports')}   ✅ Available",
                                size=14,
                                color=ft.Colors.BLUE_GREY,
                            ),
                            ft.Text(
                                facility_data.get(
                                    "description",
                                    "View details and book this facility.",
                                ),
                                size=15,
                                color=DARK,
                            ),
                            ft.Divider(),
                            ft.Text(
                                "Courts available in this facility",
                                size=17,
                                weight=ft.FontWeight.BOLD,
                                color=DARK,
                            ),
                            ft.Column(
                                spacing=5,
                                controls=court_list,
                            ),
                        ],
                    ),
                ),

                ft.Container(
                    padding=18,
                    border_radius=20,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Facility Rules",
                                size=21,
                                weight=ft.FontWeight.BOLD,
                                color=DARK,
                            ),
                            ft.Text("• Must wear appropriate athletic attire."),
                            ft.Text("• Maximum 2-hour sessions during peak hours."),
                            ft.Text("• No food or drinks except water inside the court."),
                            ft.Text("• Please arrive on time for your booking."),
                            ft.Text("• Cancellations must be made at least 2 hours in advance."),
                        ],
                    ),
                ),

                ft.ElevatedButton(
                    "Book Now",
                    bgcolor=PRIMARY,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: show_date_selection(),
                ),
            ]
        )

        page.update()

    def show_date_selection():
        content.controls.clear()

        content.controls.extend(
            [
                ft.Container(
                    padding=18,
                    border_radius=20,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        on_click=lambda e: show_info(),
                                    ),
                                    ft.Text(
                                        "Choose Booking Date",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                ],
                            ),
                            ft.Text(
                                "Enter your booking date. After that, the app will show available courts.",
                                size=14,
                                color=ft.Colors.BLUE_GREY,
                            ),
                            selected_date,
                            ft.ElevatedButton(
                                "Show Available Courts",
                                bgcolor=PRIMARY,
                                color=ft.Colors.WHITE,
                                on_click=lambda e: load_available_courts(),
                            ),
                        ],
                    ),
                )
            ]
        )

        page.update()

    def load_available_courts():
        content.controls.clear()
        content.controls.append(ft.Text("Loading available courts..."))
        page.update()

        response = api_service.get_slots(facility_id, selected_date.value)

        content.controls.clear()

        if not response.ok:
            try:
                error = response.json().get("error", "Could not load courts.")
            except Exception:
                error = "Could not load courts."

            content.controls.append(
                ft.Text(error, color=ft.Colors.RED)
            )
            page.update()
            return

        slots_data.clear()
        slots_data.update(response.json())

        show_court_selection()

    def show_court_selection():
        content.controls.clear()

        courts = slots_data.get("courts", [])

        controls = [
            ft.Container(
                padding=18,
                border_radius=20,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK,
                                    on_click=lambda e: show_date_selection(),
                                ),
                                ft.Text(
                                    "Select Court",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=DARK,
                                ),
                            ],
                        ),
                        ft.Text(
                            f"Date selected: {selected_date.value}",
                            size=14,
                            color=ft.Colors.BLUE_GREY,
                        ),
                        ft.Text(
                            slots_data.get("message", "Select a court to view available slots."),
                            size=14,
                            color=DARK,
                        ),
                    ],
                ),
            )
        ]

        if not courts:
            controls.append(
                ft.Container(
                    padding=18,
                    border_radius=20,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Text("No available courts for this date."),
                )
            )
        else:
            for court in courts:
                controls.append(
                    ft.Card(
                        elevation=3,
                        content=ft.Container(
                            padding=16,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=18,
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        height=110,
                                        border_radius=16,
                                        bgcolor=ft.Colors.BLUE_GREY_300,
                                    ),
                                    ft.Text(
                                        court.get("court_name", "Court"),
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    ft.Text(
                                        f"{court.get('sport_type', 'Sport')} • "
                                        f"Capacity: {court.get('capacity', 'N/A')}",
                                        size=14,
                                        color=ft.Colors.BLUE_GREY,
                                    ),
                                    ft.Text(
                                        f"{len(court.get('slots', []))} available slot(s)",
                                        size=13,
                                        color=PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.ElevatedButton(
                                        "View Availability",
                                        bgcolor=PRIMARY,
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, c=court: show_slots_for_court(c),
                                    ),
                                ],
                            ),
                        ),
                    )
                )

        content.controls.extend(controls)
        page.update()

    def show_slots_for_court(court):
        selected_court.clear()
        selected_court.update(court)

        content.controls.clear()

        slot_controls = []

        for slot in court.get("slots", []):
            slot_controls.append(
                ft.Container(
                    padding=14,
                    border_radius=14,
                    bgcolor="#F7F8FA",
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        f"{slot['start_time_display']} - {slot['end_time_display']}",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    ft.Text(
                                        "Available",
                                        size=12,
                                        color=ft.Colors.GREEN,
                                    ),
                                ],
                            ),
                            ft.ElevatedButton(
                                "Book",
                                bgcolor="#12B981",
                                color=ft.Colors.WHITE,
                                on_click=lambda e,
                                c=slot["court_id"],
                                s=slot["start_time"],
                                en=slot["end_time"]: book_slot(c, s, en),
                            ),
                        ],
                    ),
                )
            )

        if not slot_controls:
            slot_controls.append(
                ft.Text("No available slots for this court.", color=ft.Colors.BLUE_GREY)
            )

        content.controls.extend(
            [
                ft.Container(
                    padding=18,
                    border_radius=20,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        on_click=lambda e: show_court_selection(),
                                    ),
                                    ft.Text(
                                        "Available Slots",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                ],
                            ),
                            ft.Text(
                                court.get("court_name", "Court"),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=DARK,
                            ),
                            ft.Text(
                                f"{court.get('sport_type', 'Sport')} • {selected_date.value}",
                                size=14,
                                color=ft.Colors.BLUE_GREY,
                            ),
                            ft.Divider(),
                            ft.Column(
                                spacing=10,
                                controls=slot_controls,
                            ),
                        ],
                    ),
                )
            ]
        )

        page.update()

    def load_facility():
        content.controls.clear()
        content.controls.append(ft.Text("Loading facility details..."))
        page.update()

        response = api_service.get_facility_detail(facility_id)

        content.controls.clear()

        if not response.ok:
            content.controls.append(
                ft.Text("Could not load facility details.", color=ft.Colors.RED)
            )
            page.update()
            return

        facility_data.clear()
        facility_data.update(response.json())

        show_info()

    load_facility()

    return ft.View(
        route=f"/facility/{facility_id}",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("Facility Details", color=DARK, weight=ft.FontWeight.BOLD),
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: page.go_to("/facilities"),
            ),
        ),
        controls=[
            ft.Container(
                padding=16,
                expand=True,
                content=content,
            )
        ],
        navigation_bar=create_bottom_nav(page, 1),
    )