import math
from typing import List

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import DataTable, Footer, Header, Input, Label

from services import WifiService
from widgets import PaginationBar, ProfileDetailModal, ProfilesTable, SearchBar


class WifiManagerApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("q", "quit", "Quit", show=False),
        Binding("r", "refresh_data", "Refresh", show=True),
        Binding("left", "prev_page", "Prev Page", show=True),
        Binding("right", "next_page", "Next Page", show=True),
        Binding("slash", "focus_search", "Search", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.service = WifiService()
        self.all_profiles: List[str] = []
        self.filtered_profiles: List[str] = []
        self.current_page: int = 1
        self.page_size: int = 10

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main-container"):
            yield SearchBar()
            with Vertical(id="table-container"):
                yield ProfilesTable(id="profiles-table")
                yield PaginationBar()
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Wi-Fi Password Manager"
        self.sub_title = "Select a profile row & press Enter to view full details"

        profiles_table = self.query_one("#profiles-table", ProfilesTable)
        profiles_table.cursor_type = "row"
        profiles_table.add_column("No.", key="no", width=8)
        profiles_table.add_column("Wi-Fi SSID", key="ssid")

        self.action_refresh_data()

    def action_refresh_data(self) -> None:
        try:
            self.all_profiles = self.service.get_profiles()
            search_input = self.query_one("#search-input", Input)
            query = search_input.value.strip().lower()
            if query:
                self.filtered_profiles = [
                    p for p in self.all_profiles if query in p.lower()
                ]
            else:
                self.filtered_profiles = list(self.all_profiles)

            self.current_page = 1
            self._render_profiles_table()
            self.notify("Wi-Fi profiles loaded successfully", severity="information")
        except Exception:
            self.notify("Failed to load Wi-Fi profiles from system", severity="error")

    def _total_pages(self) -> int:
        count = len(self.filtered_profiles)
        if count == 0:
            return 1
        return math.ceil(count / self.page_size)

    def _render_profiles_table(self) -> None:
        table = self.query_one("#profiles-table", ProfilesTable)
        table.clear()

        total = len(self.filtered_profiles)
        total_pages = self._total_pages()

        if self.current_page > total_pages:
            self.current_page = max(1, total_pages)

        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        page_items = self.filtered_profiles[start:end]

        for offset, ssid in enumerate(page_items):
            no_display = str(start + offset + 1)
            table.add_row(no_display, ssid, key=f"row_{ssid}")

        page_label = self.query_one("#page-label", Label)
        page_label.update(f"Page {self.current_page} / {total_pages} (Total: {total})")

        btn_prev = self.query_one("#btn-prev")
        btn_next = self.query_one("#btn-next")
        btn_prev.disabled = self.current_page <= 1
        btn_next.disabled = self.current_page >= total_pages

    def action_prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._render_profiles_table()

    def action_next_page(self) -> None:
        if self.current_page < self._total_pages():
            self.current_page += 1
            self._render_profiles_table()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            query = event.value.strip().lower()
            if query:
                self.filtered_profiles = [
                    p for p in self.all_profiles if query in p.lower()
                ]
            else:
                self.filtered_profiles = list(self.all_profiles)
            self.current_page = 1
            self._render_profiles_table()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.query_one("#profiles-table", ProfilesTable).focus()

    def on_button_pressed(self, event) -> None:
        btn_id = event.button.id
        if btn_id == "btn-prev":
            self.action_prev_page()
        elif btn_id == "btn-next":
            self.action_next_page()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "profiles-table":
            row_key = event.row_key.value
            if row_key and row_key.startswith("row_"):
                ssid = row_key[4:]
                self._open_profile_modal(ssid)

    def _open_profile_modal(self, ssid: str) -> None:
        try:
            full_data = self.service.get_profile_full_data(ssid)
            if not full_data:
                self.notify(f"Failed to retrieve Wi-Fi details for: {ssid}", severity="warning")
                return

            self.push_screen(ProfileDetailModal(ssid, full_data))
        except Exception:
            self.notify("An error occurred while processing Wi-Fi details", severity="error")
