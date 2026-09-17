import asyncio
import math
from typing import Dict, List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input, Label, LoadingIndicator, OptionList, Static
from textual.widgets.option_list import Option
from textual.worker import Worker, WorkerState

from services import SpeedtestResult, WifiService
from widgets import (
    ConfirmDeleteModal,
    PaginationBar,
    ProfileDetailModal,
    ProfilesTable,
    SearchBar,
)


class MainMenuScreen(Screen):
    BINDINGS = [
        Binding("1", "select_profiles", "Profiles", show=False),
        Binding("2", "select_live", "Live", show=False),
        Binding("3", "select_diag", "Diag", show=False),
        Binding("4", "select_speedtest", "Speedtest", show=False),
        Binding("5", "exit_app", "Exit", show=False),
        Binding("q", "exit_app", "Quit", show=False),
        Binding("ctrl+c", "exit_app", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="menu-container"):
            yield Label("xntsh - Wi-Fi & Network Toolkit", id="menu-title")
            yield Label("Select a module using arrows & Enter, or press number keys 1-5", id="menu-subtitle")
            yield OptionList(
                Option("1. Saved Wi-Fi Profiles (Passwords, Delete, Export)", id="menu_profiles"),
                Option("2. Live Network & Nearby Scanner", id="menu_live"),
                Option("3. Hardware & IP Diagnostics", id="menu_diag"),
                Option("4. Speedtest (Download / Upload)", id="menu_speedtest"),
                Option("5. Exit", id="menu_exit"),
                id="main-options",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#main-options", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        opt_id = event.option_id
        if opt_id == "menu_profiles":
            self.action_select_profiles()
        elif opt_id == "menu_live":
            self.action_select_live()
        elif opt_id == "menu_diag":
            self.action_select_diag()
        elif opt_id == "menu_speedtest":
            self.action_select_speedtest()
        elif opt_id == "menu_exit":
            self.action_exit_app()

    def action_select_profiles(self) -> None:
        self.app.push_screen(ProfilesScreen())

    def action_select_live(self) -> None:
        self.app.push_screen(LiveNetworkScreen())

    def action_select_diag(self) -> None:
        self.app.push_screen(DiagnosticsScreen())

    def action_select_speedtest(self) -> None:
        self.app.push_screen(SpeedtestScreen())

    def action_exit_app(self) -> None:
        self.app.exit()


class ProfilesScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back to Menu", show=True),
        Binding("b", "go_back", "Back to Menu", show=False),
        Binding("r", "refresh_data", "Refresh", show=True),
        Binding("d", "delete_selected", "Delete", show=True),
        Binding("e", "export_selected", "Export", show=True),
        Binding("left", "prev_page", "Prev Page", show=True),
        Binding("right", "next_page", "Next Page", show=True),
        Binding("slash", "focus_search", "Search", show=True),
        Binding("ctrl+c", "exit_app", "Quit", show=True),
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
        with Vertical(id="profiles-container"):
            yield SearchBar()
            with Vertical(id="table-container"):
                yield ProfilesTable(id="profiles-table")
                yield PaginationBar()
        yield Footer()

    def on_mount(self) -> None:
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
            self.notify("Wi-Fi profiles loaded", severity="information")
        except Exception:
            self.notify("Failed to query profiles", severity="error")

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

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_exit_app(self) -> None:
        self.app.exit()

    def _get_highlighted_ssid(self) -> Optional[str]:
        table = self.query_one("#profiles-table", ProfilesTable)
        if table.row_count == 0 or table.cursor_row is None:
            return None
        start = (self.current_page - 1) * self.page_size
        target_idx = start + table.cursor_row
        if 0 <= target_idx < len(self.filtered_profiles):
            return self.filtered_profiles[target_idx]
        return None

    def action_delete_selected(self) -> None:
        ssid = self._get_highlighted_ssid()
        if not ssid:
            self.notify("No Wi-Fi profile selected", severity="warning")
            return

        def handle_delete(confirmed: Optional[bool]) -> None:
            if confirmed:
                ok = self.service.delete_profile(ssid)
                if ok:
                    self.notify(f"Profile '{ssid}' deleted", severity="information")
                    self.action_refresh_data()
                else:
                    self.notify(f"Failed to delete profile '{ssid}'", severity="error")

        self.app.push_screen(ConfirmDeleteModal(ssid), handle_delete)

    def action_export_selected(self) -> None:
        ssid = self._get_highlighted_ssid()
        if not ssid:
            self.notify("No Wi-Fi profile selected", severity="warning")
            return
        ok, msg = self.service.export_profile(ssid)
        if ok:
            self.notify(f"Profile exported: {msg}", severity="information")
        else:
            self.notify(f"Export failed: {msg}", severity="error")

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
                self.notify(f"Failed to retrieve details for: {ssid}", severity="warning")
                return
            self.app.push_screen(ProfileDetailModal(ssid, full_data))
        except Exception:
            self.notify("An error occurred while reading profile details", severity="error")


class LiveNetworkScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back to Menu", show=True),
        Binding("b", "go_back", "Back to Menu", show=False),
        Binding("r", "refresh_live", "Rescan", show=True),
        Binding("ctrl+c", "exit_app", "Quit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.service = WifiService()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="live-container"):
            yield Label("Active Interface Status", id="active-title")
            with Container(id="active-card"):
                yield Label("Loading active connection...", id="active-status-label")
            yield Label("Nearby Wi-Fi Networks", id="nearby-title")
            yield DataTable(id="nearby-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#nearby-table", DataTable)
        table.cursor_type = "row"
        table.add_column("SSID", key="n_ssid")
        table.add_column("Signal", key="n_sig", width=10)
        table.add_column("Channel", key="n_ch", width=10)
        table.add_column("Band", key="n_band", width=12)
        table.add_column("Security", key="n_sec")
        table.add_column("BSSID", key="n_bssid")
        self.action_refresh_live()

    def action_refresh_live(self) -> None:
        try:
            info = self.service.get_active_interface()
            status_lbl = self.query_one("#active-status-label", Label)
            if info:
                state = info.get("State", "Unknown")
                ssid = info.get("SSID", "-")
                signal = info.get("Signal", "-")
                band = info.get("Band", "-")
                channel = info.get("Channel", "-")
                rx = info.get("Receive rate (Mbps)", "-")
                tx = info.get("Transmit rate (Mbps)", "-")
                status_lbl.update(
                    f"State: {state} | SSID: {ssid} | Signal: {signal} | Band: {band} (Ch {channel}) | Rx: {rx} Mbps / Tx: {tx} Mbps"
                )
            else:
                status_lbl.update("No active Wi-Fi interface detected.")

            networks = self.service.get_nearby_networks()
            table = self.query_one("#nearby-table", DataTable)
            table.clear()
            for net in networks:
                table.add_row(
                    net.get("ssid", "-"),
                    net.get("signal", "-"),
                    net.get("channel", "-"),
                    net.get("band", "-"),
                    f"{net.get('auth', '-')} / {net.get('encryption', '-')}",
                    net.get("bssid", "-"),
                )
            self.notify(f"Scan complete: {len(networks)} visible networks", severity="information")
        except Exception:
            self.notify("Failed to scan live network", severity="error")

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_exit_app(self) -> None:
        self.app.exit()


class DiagnosticsScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back to Menu", show=True),
        Binding("b", "go_back", "Back to Menu", show=False),
        Binding("r", "refresh_diag", "Refresh", show=True),
        Binding("ctrl+c", "exit_app", "Quit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.service = WifiService()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="diag-container"):
            yield Label("Wi-Fi Driver & Hardware Info", id="driver-title")
            yield DataTable(id="driver-table")
            yield Label("IPv4 & DNS Configuration", id="ipv4-title")
            yield DataTable(id="ipv4-table")
        yield Footer()

    def on_mount(self) -> None:
        drv_table = self.query_one("#driver-table", DataTable)
        drv_table.cursor_type = "row"
        drv_table.add_column("Property", key="prop", width=34)
        drv_table.add_column("Value", key="val")

        ip_table = self.query_one("#ipv4-table", DataTable)
        ip_table.cursor_type = "row"
        ip_table.add_column("Interface", key="iface", width=22)
        ip_table.add_column("DHCP", key="dhcp", width=8)
        ip_table.add_column("IP Address", key="ip", width=18)
        ip_table.add_column("Subnet", key="sub", width=20)
        ip_table.add_column("Gateway", key="gw", width=16)
        ip_table.add_column("DNS Servers", key="dns")

        self.action_refresh_diag()

    def action_refresh_diag(self) -> None:
        try:
            drv_info = self.service.get_driver_info()
            drv_table = self.query_one("#driver-table", DataTable)
            drv_table.clear()
            for k, v in drv_info:
                drv_table.add_row(k, v)

            ipv4_configs = self.service.get_ipv4_configs()
            ip_table = self.query_one("#ipv4-table", DataTable)
            ip_table.clear()
            for cfg in ipv4_configs:
                ip_table.add_row(
                    cfg.get("name", "-"),
                    cfg.get("dhcp", "-"),
                    cfg.get("ip", "-"),
                    cfg.get("subnet", "-"),
                    cfg.get("gateway", "-"),
                    cfg.get("dns", "-"),
                )
            self.notify("Diagnostics data loaded", severity="information")
        except Exception:
            self.notify("Failed to load network diagnostics", severity="error")

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_exit_app(self) -> None:
        self.app.exit()


class SpeedtestScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back to Menu", show=True),
        Binding("b", "go_back", "Back to Menu", show=False),
        Binding("enter", "start_test", "Run (5x)", show=True, priority=True),
        Binding("r", "start_test", "Re-run", show=False, priority=True),
        Binding("s", "stop_test", "Stop", show=True, priority=True),
        Binding("ctrl+c", "exit_app", "Quit", show=True),
    ]

    TOTAL_ITERATIONS: int = 5

    def __init__(self) -> None:
        super().__init__()
        self.service = WifiService()
        self.results: List[SpeedtestResult] = []
        self._test_in_progress = False
        self._stop_requested = False
        self._speedtest_worker: Optional[Worker] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="speedtest-container"):
            yield Label("Speedtest", id="speedtest-title")
            yield Label(f"Press Enter to start speedtest ({self.TOTAL_ITERATIONS} iterations) | Press 's' to stop", id="speedtest-status")
            yield LoadingIndicator(id="speedtest-loader")
            yield Label("Summary", id="summary-title")
            yield DataTable(id="summary-table")
            yield Label("History (this session)", id="history-title")
            yield DataTable(id="history-table")
        yield Footer()

    def on_mount(self) -> None:
        loader = self.query_one("#speedtest-loader", LoadingIndicator)
        loader.display = False

        summary = self.query_one("#summary-table", DataTable)
        summary.cursor_type = "row"
        summary.add_column("Metric", key="metric", width=12)
        summary.add_column("Download (Mbps)", key="dl", width=18)
        summary.add_column("Upload (Mbps)", key="ul", width=18)
        summary.add_column("Ping (ms)", key="ping", width=12)
        summary.add_row("Latest", "-", "-", "-", key="row_latest")
        summary.add_row("Highest", "-", "-", "-", key="row_highest")
        summary.add_row("Lowest", "-", "-", "-", key="row_lowest")
        summary.add_row("Average", "-", "-", "-", key="row_average")

        history = self.query_one("#history-table", DataTable)
        history.cursor_type = "row"
        history.add_column("No.", key="h_no", width=6)
        history.add_column("Time", key="h_time", width=12)
        history.add_column("Download (Mbps)", key="h_dl", width=18)
        history.add_column("Upload (Mbps)", key="h_ul", width=18)
        history.add_column("Ping (ms)", key="h_ping", width=12)
        history.add_column("Server", key="h_srv")

    def action_start_test(self) -> None:
        if self._test_in_progress:
            self.notify("Speedtest already running, please wait...", severity="warning")
            return

        self._test_in_progress = True
        self._stop_requested = False
        status = self.query_one("#speedtest-status", Label)
        status.update(f"Starting batch speedtest (1/{self.TOTAL_ITERATIONS})...")
        loader = self.query_one("#speedtest-loader", LoadingIndicator)
        loader.display = True

        self._speedtest_worker = self.run_worker(
            self._run_batch_speedtest,
            exclusive=True,
            exit_on_error=False,
        )

    def action_stop_test(self) -> None:
        if not self._test_in_progress:
            self.notify("No speedtest currently running", severity="warning")
            return

        self._stop_requested = True
        if self._speedtest_worker is not None:
            self._speedtest_worker.cancel()
        self._test_in_progress = False
        self.query_one("#speedtest-loader", LoadingIndicator).display = False
        status = self.query_one("#speedtest-status", Label)
        status.update(f"Speedtest stopped ({len(self.results)} runs recorded). Press Enter to start.")
        self.notify("Speedtest stopped by user", severity="warning")

    async def _run_batch_speedtest(self) -> None:
        status = self.query_one("#speedtest-status", Label)
        loader = self.query_one("#speedtest-loader", LoadingIndicator)
        completed_count = 0

        for i in range(1, self.TOTAL_ITERATIONS + 1):
            if self._stop_requested:
                break

            status.update(f"Running speedtest iteration {i}/{self.TOTAL_ITERATIONS}... [Press 's' to stop]")

            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(self.service.run_speedtest),
                    timeout=25.0,
                )
            except asyncio.CancelledError:
                break
            except asyncio.TimeoutError:
                self.notify(f"Iteration {i}/{self.TOTAL_ITERATIONS} timed out", severity="error")
                result = None
            except Exception:
                result = None

            if self._stop_requested:
                break

            if result is not None:
                self.results.append(result)
                completed_count += 1
                self._update_summary()
                self._update_history()
                status.update(
                    f"Iteration {i}/{self.TOTAL_ITERATIONS} complete: "
                    f"{result.download_mbps} Mbps down / {result.upload_mbps} Mbps up / {result.ping_ms} ms ping"
                )
            else:
                status.update(f"Iteration {i}/{self.TOTAL_ITERATIONS} failed.")
                self.notify(f"Iteration {i}/{self.TOTAL_ITERATIONS} failed to connect", severity="error")

            if i < self.TOTAL_ITERATIONS and not self._stop_requested:
                try:
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    break

        loader.display = False
        self._test_in_progress = False

        if self._stop_requested:
            status.update(f"Speedtest stopped ({completed_count} iterations completed). Press Enter to re-run.")
            self.notify(f"Speedtest stopped after {completed_count} runs", severity="warning")
        elif completed_count == self.TOTAL_ITERATIONS:
            status.update(f"Batch completed ({completed_count}/{self.TOTAL_ITERATIONS}). Press Enter to re-run.")
            self.notify(f"Batch speedtest completed ({completed_count} runs)", severity="information")
        else:
            status.update(f"Batch finished with {completed_count}/{self.TOTAL_ITERATIONS} successful runs. Press Enter to re-run.")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker is not self._speedtest_worker:
            return

        if event.state in (WorkerState.ERROR, WorkerState.CANCELLED):
            self._test_in_progress = False
            self.query_one("#speedtest-loader", LoadingIndicator).display = False
            if event.state == WorkerState.ERROR:
                status = self.query_one("#speedtest-status", Label)
                status.update("Speedtest encountered an error. Press Enter to retry.")
                self.notify("Speedtest encountered an error", severity="error")

    def _update_summary(self) -> None:
        if not self.results:
            return

        table = self.query_one("#summary-table", DataTable)
        latest = self.results[-1]

        dl_vals = [r.download_mbps for r in self.results]
        ul_vals = [r.upload_mbps for r in self.results]
        ping_vals = [r.ping_ms for r in self.results]

        table.update_cell("row_latest", "dl", str(latest.download_mbps))
        table.update_cell("row_latest", "ul", str(latest.upload_mbps))
        table.update_cell("row_latest", "ping", str(latest.ping_ms))

        table.update_cell("row_highest", "dl", str(max(dl_vals)))
        table.update_cell("row_highest", "ul", str(max(ul_vals)))
        table.update_cell("row_highest", "ping", str(min(ping_vals)))

        table.update_cell("row_lowest", "dl", str(min(dl_vals)))
        table.update_cell("row_lowest", "ul", str(min(ul_vals)))
        table.update_cell("row_lowest", "ping", str(max(ping_vals)))

        count = len(self.results)
        table.update_cell("row_average", "dl", str(round(sum(dl_vals) / count, 2)))
        table.update_cell("row_average", "ul", str(round(sum(ul_vals) / count, 2)))
        table.update_cell("row_average", "ping", str(round(sum(ping_vals) / count, 2)))

    def _update_history(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.clear()
        for idx, r in enumerate(self.results):
            table.add_row(
                str(idx + 1),
                r.timestamp,
                str(r.download_mbps),
                str(r.upload_mbps),
                str(r.ping_ms),
                r.server,
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_exit_app(self) -> None:
        self.app.exit()
