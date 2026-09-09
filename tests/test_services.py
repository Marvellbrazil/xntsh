import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import WifiService


def test_parser_sample_profiles():
    service = WifiService()
    sample_output = """
Profiles on interface Wi-Fi:

User profiles
-------------
    All User Profile     : Home-Wifi
    All User Profile     : Office-Guest
    All User Profile     : Cafe_Free
"""
    original_run = service._run_command
    service._run_command = lambda args: sample_output

    profiles = service.get_profiles()
    assert profiles == ["Home-Wifi", "Office-Guest", "Cafe_Free"]

    service._run_command = original_run


def test_parser_sample_full_data():
    service = WifiService()
    sample_output = """
Profile Home-Wifi on interface Wi-Fi:
=======================================================================
Applied: All User Profile

Profile information
-------------------
    Version                : 1
    Type                   : Wireless LAN
    Name                   : Home-Wifi

Connectivity settings
---------------------
    SSID name              : "Home-Wifi"
    Network type           : Infrastructure

Security settings
-----------------
    Authentication         : WPA2-Personal
    Cipher                 : CCMP
    Security key           : Present
    Key Content            : mysecretpassword123
"""
    original_run = service._run_command
    service._run_command = lambda args: sample_output

    full_data = service.get_profile_full_data("Home-Wifi")
    assert len(full_data) > 0
    assert full_data[0][0] == "PASSWORD (Key Content)"
    assert full_data[0][1] == "mysecretpassword123"

    labels = [item[0] for item in full_data]
    assert any("Authentication" in lbl for lbl in labels)
    assert any("Network type" in lbl for lbl in labels)

    service._run_command = original_run


def test_parser_empty_and_error():
    service = WifiService()
    original_run = service._run_command
    service._run_command = lambda args: ""

    assert service.get_profiles() == []
    assert service.get_profile_full_data("NotExisting") == []
    assert service.get_profile_full_data("") == []

    service._run_command = original_run


def test_live_windows():
    service = WifiService()
    profiles = service.get_profiles()
    assert isinstance(profiles, list)
    if profiles:
        full_data = service.get_profile_full_data(profiles[0])
        assert isinstance(full_data, list)
        assert len(full_data) > 0
        assert full_data[0][0] == "PASSWORD (Key Content)"


if __name__ == "__main__":
    test_parser_sample_profiles()
    test_parser_sample_full_data()
    test_parser_empty_and_error()
    test_live_windows()
    print("ALL SERVICE TESTS PASSED")
