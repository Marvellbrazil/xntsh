import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import WifiManagerApp
from screens import DiagnosticsScreen, LiveNetworkScreen, MainMenuScreen, ProfilesScreen
from widgets import ProfileDetailModal, ProfilesTable


async def test_multi_menu_flow():
    app = WifiManagerApp()
    async with app.run_test() as pilot:
        assert isinstance(app.screen, MainMenuScreen)

        await pilot.press("1")
        await pilot.pause()
        assert isinstance(app.screen, ProfilesScreen)

        table = app.screen.query_one("#profiles-table", ProfilesTable)
        assert table.row_count > 0

        search = app.screen.query_one("#search-input")
        search.value = "nonexistentwifi999"
        await pilot.pause()
        assert table.row_count == 0

        search.value = ""
        await pilot.pause()
        assert table.row_count > 0

        table.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ProfileDetailModal)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, ProfilesScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)

        await pilot.press("2")
        await pilot.pause()
        assert isinstance(app.screen, LiveNetworkScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)

        await pilot.press("3")
        await pilot.pause()
        assert isinstance(app.screen, DiagnosticsScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)


if __name__ == "__main__":
    asyncio.run(test_multi_menu_flow())
    print("ALL APP MULTI-MENU TESTS PASSED")
