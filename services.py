import os
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class ProfileDetail:
    ssid: str
    network_type: str
    authentication: str
    cipher: str
    security_key: str
    password: str


class WifiService:
    @staticmethod
    def _run_command(args: List[str]) -> str:
        flags = 0
        if os.name == "nt":
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            errors="replace",
            creationflags=flags,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout

    def get_profiles(self) -> List[str]:
        output = self._run_command(["netsh", "wlan", "show", "profile"])
        if not output:
            return []

        profiles = []
        for line in output.splitlines():
            line_str = line.strip()
            if ":" in line_str:
                parts = line_str.split(":", 1)
                left = parts[0].strip().lower()
                if "all user profile" in left or "profil semua pengguna" in left or "profile" in left:
                    name = parts[1].strip()
                    if name and name not in profiles:
                        profiles.append(name)
        return profiles

    def get_profile_full_data(self, ssid: str) -> List[Tuple[str, str]]:
        if not ssid or not ssid.strip():
            return []

        clean_ssid = ssid.strip()
        output = self._run_command(
            ["netsh", "wlan", "show", "profile", f"name={clean_ssid}", "key=clear"]
        )
        if not output:
            return []

        key_value_pairs: List[Tuple[str, str]] = []
        password_entry: Optional[Tuple[str, str]] = None
        current_section = ""

        for line in output.splitlines():
            trimmed = line.strip()
            if not trimmed or trimmed.startswith("---") or trimmed.startswith("==="):
                continue

            if ":" not in trimmed:
                current_section = trimmed
                continue

            parts = trimmed.split(":", 1)
            raw_key = parts[0].strip()
            val = parts[1].strip()

            label = f"[{current_section}] {raw_key}" if current_section else raw_key

            if raw_key.lower() in ("key content", "konten kunci"):
                password_entry = ("PASSWORD (Key Content)", val if val else "-")
            else:
                key_value_pairs.append((label, val if val else "-"))

        if password_entry is not None:
            key_value_pairs.insert(0, password_entry)
        else:
            key_value_pairs.insert(0, ("PASSWORD (Key Content)", "- (None / Protected)"))

        return key_value_pairs

    def delete_profile(self, ssid: str) -> bool:
        if not ssid or not ssid.strip():
            return False

        clean_ssid = ssid.strip()
        output = self._run_command(["netsh", "wlan", "delete", "profile", f"name={clean_ssid}"])
        return "deleted" in output.lower() or "dihapus" in output.lower()

    def export_profile(self, ssid: str, folder_path: str = ".") -> Tuple[bool, str]:
        if not ssid or not ssid.strip():
            return False, "SSID is empty"

        clean_ssid = ssid.strip()
        abs_folder = os.path.abspath(folder_path)
        output = self._run_command([
            "netsh", "wlan", "export", "profile",
            f"name={clean_ssid}",
            f"folder={abs_folder}",
            "key=clear"
        ])
        if "successfully" in output.lower() or "berhasil" in output.lower() or f"{clean_ssid}.xml" in output:
            return True, f"Saved to {abs_folder}"
        return False, "Export command failed"

    def get_active_interface(self) -> Dict[str, str]:
        output = self._run_command(["netsh", "wlan", "show", "interfaces"])
        if not output:
            return {}

        info: Dict[str, str] = {}
        for line in output.splitlines():
            trimmed = line.strip()
            if ":" not in trimmed:
                continue
            parts = trimmed.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            info[key] = val
        return info

    def get_nearby_networks(self) -> List[Dict[str, str]]:
        output = self._run_command(["netsh", "wlan", "show", "networks", "mode=bssid"])
        if not output:
            return []

        networks: List[Dict[str, str]] = []
        current: Optional[Dict[str, str]] = None

        for line in output.splitlines():
            trimmed = line.strip()
            if trimmed.startswith("SSID") and ":" in trimmed:
                if current and current.get("ssid"):
                    networks.append(current)
                ssid_val = trimmed.split(":", 1)[1].strip()
                current = {
                    "ssid": ssid_val if ssid_val else "<Hidden SSID>",
                    "auth": "-",
                    "encryption": "-",
                    "signal": "-",
                    "channel": "-",
                    "band": "-",
                    "radio": "-",
                    "bssid": "-",
                }
            elif current is not None and ":" in trimmed:
                parts = trimmed.split(":", 1)
                k = parts[0].strip().lower()
                v = parts[1].strip()
                if "authentication" in k:
                    current["auth"] = v
                elif "encryption" in k:
                    current["encryption"] = v
                elif "signal" in k:
                    current["signal"] = v
                elif "channel" in k:
                    current["channel"] = v
                elif "band" in k:
                    current["band"] = v
                elif "radio type" in k:
                    current["radio"] = v
                elif "bssid" in k:
                    current["bssid"] = v

        if current and current.get("ssid"):
            networks.append(current)

        return networks

    def get_driver_info(self) -> List[Tuple[str, str]]:
        output = self._run_command(["netsh", "wlan", "show", "drivers"])
        if not output:
            return []

        details: List[Tuple[str, str]] = []
        for line in output.splitlines():
            trimmed = line.strip()
            if ":" not in trimmed:
                continue
            parts = trimmed.split(":", 1)
            k = parts[0].strip()
            v = parts[1].strip()
            if k:
                details.append((k, v if v else "-"))
        return details

    def get_ipv4_configs(self) -> List[Dict[str, str]]:
        output = self._run_command(["netsh", "interface", "ipv4", "show", "config"])
        if not output:
            return []

        interfaces: List[Dict[str, str]] = []
        current: Optional[Dict[str, str]] = None

        for line in output.splitlines():
            trimmed = line.strip()
            if trimmed.startswith("Configuration for interface"):
                if current and current.get("name"):
                    interfaces.append(current)
                name = trimmed.replace("Configuration for interface", "").strip().strip('"')
                current = {
                    "name": name,
                    "dhcp": "-",
                    "ip": "-",
                    "subnet": "-",
                    "gateway": "-",
                    "dns": "-",
                }
            elif current is not None and ":" in trimmed:
                parts = trimmed.split(":", 1)
                k = parts[0].strip().lower()
                v = parts[1].strip()
                if "dhcp enabled" in k:
                    current["dhcp"] = v
                elif "ip address" in k and current["ip"] == "-":
                    current["ip"] = v
                elif "subnet" in k:
                    current["subnet"] = v
                elif "default gateway" in k:
                    current["gateway"] = v
                elif "dns servers" in k:
                    current["dns"] = v
            elif current is not None and current["dns"] != "-" and trimmed and ":" not in trimmed:
                current["dns"] += f", {trimmed}"

        if current and current.get("name"):
            interfaces.append(current)

        return interfaces
