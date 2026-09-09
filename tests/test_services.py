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


def test_delete_and_export():
    service = WifiService()
    original_run = service._run_command

    service._run_command = lambda args: 'Profile "TestSSID" is deleted from interface "Wi-Fi".'
    assert service.delete_profile("TestSSID") is True

    service._run_command = lambda args: "The profile is exported successfully to folder C:\\test."
    ok, _ = service.export_profile("TestSSID")
    assert ok is True

    service._run_command = original_run


def test_active_interface_parser():
    service = WifiService()
    sample_output = """
There is 1 interface on the system:

    Name                   : Wi-Fi
    State                  : connected
    SSID                   : MyNetwork
    Band                   : 5 GHz
    Channel                : 36
    Receive rate (Mbps)    : 866
    Transmit rate (Mbps)   : 866
    Signal                 : 95%
"""
    original_run = service._run_command
    service._run_command = lambda args: sample_output

    info = service.get_active_interface()
    assert info.get("Name") == "Wi-Fi"
    assert info.get("State") == "connected"
    assert info.get("SSID") == "MyNetwork"
    assert info.get("Signal") == "95%"

    service._run_command = original_run


def test_nearby_networks_parser():
    service = WifiService()
    sample_output = """
Interface name : Wi-Fi
There are 2 networks currently visible.

SSID 1 : Cafe-WiFi
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 11:22:33:44:55:66
         Signal             : 82%
         Band               : 5 GHz
         Channel            : 40

SSID 2 : Public-Open
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Signal             : 60%
         Band               : 2.4 GHz
         Channel            : 6
"""
    original_run = service._run_command
    service._run_command = lambda args: sample_output

    nets = service.get_nearby_networks()
    assert len(nets) == 2
    assert nets[0]["ssid"] == "Cafe-WiFi"
    assert nets[0]["signal"] == "82%"
    assert nets[1]["ssid"] == "Public-Open"
    assert nets[1]["auth"] == "Open"

    service._run_command = original_run


def test_ipv4_configs_parser():
    service = WifiService()
    sample_output = """
Configuration for interface "Wi-Fi"
    DHCP enabled:                         Yes
    IP Address:                           192.168.1.50
    Subnet Prefix:                        192.168.1.0/24 (mask 255.255.255.0)
    Default Gateway:                      192.168.1.1
    DNS servers configured through DHCP:  1.1.1.1
                                          8.8.8.8
"""
    original_run = service._run_command
    service._run_command = lambda args: sample_output

    configs = service.get_ipv4_configs()
    assert len(configs) == 1
    assert configs[0]["name"] == "Wi-Fi"
    assert configs[0]["dhcp"] == "Yes"
    assert configs[0]["ip"] == "192.168.1.50"
    assert "1.1.1.1" in configs[0]["dns"]

    service._run_command = original_run


def test_live_windows():
    service = WifiService()
    profiles = service.get_profiles()
    assert isinstance(profiles, list)
    if profiles:
        full_data = service.get_profile_full_data(profiles[0])
        assert isinstance(full_data, list)
        assert len(full_data) > 0


if __name__ == "__main__":
    test_parser_sample_profiles()
    test_parser_sample_full_data()
    test_delete_and_export()
    test_active_interface_parser()
    test_nearby_networks_parser()
    test_ipv4_configs_parser()
    test_live_windows()
    print("ALL SERVICE TESTS PASSED")
