import flet as ft
from datetime import datetime


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


def is_expired(booking):
    try:
        booking_date = booking.get("booking_date")
        end_time = booking.get("end_time")

        booking_end = datetime.strptime(
            f"{booking_date} {end_time}",
            "%Y-%m-%d %H:%M",
        )

        return booking_end < datetime.now()

    except Exception:
        return False


def status_badge(text, color):
    return ft.Container(
        content=ft.Text(
            text.upper(),
            size=11,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
        ),
        bgcolor=color,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=20,
    )


def filter_button(title, selected, on_click):
    return ft.ElevatedButton(
        title,
        bgcolor=PRIMARY if selected else ft.Colors.WHITE,
        color=ft.Colors.WHITE if selected else DARK,
        on_click=on_click,
    )


def booking_card(page, booking, api_service, reload_fn, booking_type):
    booking_id = booking.get("booking_id")
    status = booking.get("status", "confirmed")

    if booking_type == "upcoming":
        badge = status_badge("Upcoming", ft.Colors.GREEN)
    elif booking_type == "cancelled":
        badge = status_badge("Cancelled", ft.Colors.RED)
    else:
        badge = status_badge("Expired", ft.Colors.BLUE_GREY)

    def cancel_booking(e):
        response = api_service.cancel_booking(booking_id)

        if response.ok:
            show_snack(page, "Booking cancelled successfully.", ft.Colors.GREEN)
            reload_fn()
        else:
            show_snack(page, "Could not cancel booking.", ft.Colors.RED)

    card_controls = [
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    booking.get("facility_name", "Facility"),
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=DARK,
                ),
                badge,
            ],
        ),
        ft.Text(
            f"Court: {booking.get('court_name', 'N/A')}",
            size=14,
            color=ft.Colors.BLUE_GREY,
        ),
        ft.Text(
            f"📅 Date: {booking.get('booking_date', 'N/A')}",
            size=14,
            color=DARK,
        ),
        ft.Text(
            f"⏰ Time: {booking.get('time_display', 'N/A')}",
            size=14,
            color=DARK,
        ),
    ]

    if booking_type == "upcoming":
        card_controls.append(
            ft.ElevatedButton(
                "Cancel Booking",
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                on_click=cancel_booking,
            )
        )

    return ft.Card(
        elevation=3,
        content=ft.Container(
            padding=16,
            border_radius=18,
            bgcolor=ft.Colors.WHITE,
            content=ft.Column(
                spacing=10,
                controls=card_controls,
            ),
        ),
    )


def create_bookings_view(page, api_service):
    selected_tab = {"value": "upcoming"}

    bookings_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=14,
    )

    summary_text = ft.Text("", size=13, color=DARK)

    tabs_row = ft.Row(
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        controls=[],
    )

    all_bookings = {
        "upcoming": [],
        "cancelled": [],
        "expired": [],
    }

    def set_tab(tab):
        selected_tab["value"] = tab
        render_tabs()
        render_bookings()

    def render_tabs():
        tabs_row.controls.clear()

        tabs_row.controls.extend(
            [
                filter_button(
                    f"Upcoming ({len(all_bookings['upcoming'])})",
                    selected_tab["value"] == "upcoming",
                    lambda e: set_tab("upcoming"),
                ),
                filter_button(
                    f"Cancelled ({len(all_bookings['cancelled'])})",
                    selected_tab["value"] == "cancelled",
                    lambda e: set_tab("cancelled"),
                ),
                filter_button(
                    f"Expired ({len(all_bookings['expired'])})",
                    selected_tab["value"] == "expired",
                    lambda e: set_tab("expired"),
                ),
            ]
        )

    def render_bookings():
        bookings_column.controls.clear()

        current_tab = selected_tab["value"]
        bookings = all_bookings[current_tab]

        title = {
            "upcoming": "Upcoming Bookings",
            "cancelled": "Cancelled Bookings",
            "expired": "Expired Bookings",
        }.get(current_tab, "Bookings")

        bookings_column.controls.append(
            ft.Text(
                title,
                size=20,
                weight=ft.FontWeight.BOLD,
                color=DARK,
            )
        )

        if not bookings:
            bookings_column.controls.append(
                ft.Container(
                    padding=20,
                    border_radius=18,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(
                                ft.Icons.EVENT_BUSY,
                                size=45,
                                color=ft.Colors.BLUE_GREY,
                            ),
                            ft.Text(
                                "No bookings found here.",
                                size=15,
                                color=ft.Colors.BLUE_GREY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.ElevatedButton(
                                "Browse Facilities",
                                bgcolor=PRIMARY,
                                color=ft.Colors.WHITE,
                                on_click=lambda e: page.go_to("/facilities"),
                            ),
                        ],
                    ),
                )
            )
            page.update()
            return

        for booking in bookings:
            bookings_column.controls.append(
                booking_card(
                    page,
                    booking,
                    api_service,
                    load_bookings,
                    current_tab,
                )
            )

        page.update()

    def split_bookings(bookings):
        all_bookings["upcoming"].clear()
        all_bookings["cancelled"].clear()
        all_bookings["expired"].clear()

        for booking in bookings:
            status = (booking.get("status") or "").lower()

            if status == "cancelled":
                all_bookings["cancelled"].append(booking)
            elif is_expired(booking):
                all_bookings["expired"].append(booking)
            else:
                all_bookings["upcoming"].append(booking)

    def load_bookings():
        bookings_column.controls.clear()
        bookings_column.controls.append(ft.Text("Loading bookings..."))
        page.update()

        try:
            response = api_service.get_my_bookings()

            bookings_column.controls.clear()

            if not response.ok:
                bookings_column.controls.append(
                    ft.Text("Could not load bookings.", color=ft.Colors.RED)
                )
                page.update()
                return

            bookings = response.json()

            split_bookings(bookings)

            total = len(bookings)
            upcoming = len(all_bookings["upcoming"])
            cancelled = len(all_bookings["cancelled"])
            expired = len(all_bookings["expired"])

            summary_text.value = (
                f"Total: {total} • Upcoming: {upcoming} • "
                f"Cancelled: {cancelled} • Expired: {expired}"
            )

            render_tabs()
            render_bookings()

        except Exception as ex:
            bookings_column.controls.clear()
            bookings_column.controls.append(
                ft.Text(f"Error: {ex}", color=ft.Colors.RED)
            )
            page.update()

    render_tabs()
    load_bookings()

    return ft.View(
        route="/bookings",
        bgcolor=BG,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("My Bookings", color=DARK, weight=ft.FontWeight.BOLD),
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
                        ft.Container(
                            padding=16,
                            border_radius=18,
                            bgcolor="#EAF7FF",
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "Booking Summary",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK,
                                    ),
                                    summary_text,
                                ],
                            ),
                        ),
                        tabs_row,
                        bookings_column,
                    ],
                ),
            )
        ],
        navigation_bar=create_bottom_nav(page, 2),
    )