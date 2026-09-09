from typing import List, Tuple

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label


class SearchBar(Container):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Search Wi-Fi SSID... (Press / to focus)",
            id="search-input",
        )


class PaginationBar(Horizontal):
    def compose(self) -> ComposeResult:
        yield Button("◀ Previous", id="btn-prev", variant="default")
        yield Label("Page 1 / 1", id="page-label")
        yield Button("Next ▶", id="btn-next", variant="default")


class ProfilesTable(DataTable):
    pass


class ProfileDetailModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss_modal", "Close"),
        Binding("ctrl+c", "dismiss_modal", "Close"),
        Binding("enter", "dismiss_modal", "Close"),
    ]

    def __init__(self, ssid: str, details: List[Tuple[str, str]]) -> None:
        super().__init__()
        self.ssid = ssid
        self.details = details

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog-container"):
            yield Label(f"Wi-Fi Profile Details: {self.ssid}", id="modal-title")
            yield DataTable(id="modal-table")
            with Horizontal(id="modal-actions"):
                yield Button("Close [Esc]", id="btn-close", variant="error")

    def on_mount(self) -> None:
        table = self.query_one("#modal-table", DataTable)
        table.cursor_type = "row"
        table.add_column("Parameter", key="param", width=38)
        table.add_column("Value", key="val")

        for param, val in self.details:
            table.add_row(param, val)

        self.query_one("#btn-close", Button).focus()

    def action_dismiss_modal(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()
