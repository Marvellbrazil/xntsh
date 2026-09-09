import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import WifiManagerApp
from widgets import ProfileDetailModal, ProfilesTable


async def test_app_flow():
    app = WifiManagerApp()
    async with app.run_test() as pilot:
        table = app.query_one("#profiles-table", ProfilesTable)
        assert table.row_count > 0

        search = app.query_one("#search-input")
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
        modal_table = app.screen.query_one("#modal-table")
        assert modal_table.row_count > 0
        close_btn = app.screen.query_one("#btn-close")
        assert close_btn.variant == "error"

        await pilot.press("ctrl+c")
        await pilot.pause()

        assert not isinstance(app.screen, ProfileDetailModal)

        await pilot.click("#btn-next")
        await pilot.pause()
        await pilot.click("#btn-prev")
        await pilot.pause()


if __name__ == "__main__":
    asyncio.run(test_app_flow())
    print("ALL APP TESTS PASSED")
