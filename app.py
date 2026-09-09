from textual.app import App
from textual.binding import Binding

from screens import MainMenuScreen


class WifiManagerApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
    ]

    def on_mount(self) -> None:
        self.title = "xntsh"
        self.sub_title = "Wi-Fi & Network Toolkit"
        self.push_screen(MainMenuScreen())
