import os
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple


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

    def get_profile_detail(self, ssid: str) -> Optional[ProfileDetail]:
        if not ssid or not ssid.strip():
            return None

        clean_ssid = ssid.strip()
        output = self._run_command(
            ["netsh", "wlan", "show", "profile", f"name={clean_ssid}", "key=clear"]
        )
        if not output:
            return None

        data = {
            "ssid": clean_ssid,
            "network_type": "Unknown",
            "authentication": "Unknown",
            "cipher": "Unknown",
            "security_key": "Unknown",
            "password": "-",
        }

        auth_list = []
        cipher_list = []

        for line in output.splitlines():
            line_str = line.strip()
            if ":" not in line_str:
                continue

            parts = line_str.split(":", 1)
            key = parts[0].strip().lower()
            val = parts[1].strip()

            if "ssid name" in key:
                data["ssid"] = val.strip('"')
            elif "network type" in key or "tipe jaringan" in key:
                data["network_type"] = val
            elif "authentication" in key or "autentikasi" in key:
                if val and val not in auth_list:
                    auth_list.append(val)
            elif "cipher" in key:
                if val and val not in cipher_list:
                    cipher_list.append(val)
            elif "security key" in key or "kunci keamanan" in key:
                data["security_key"] = val
            elif "key content" in key or "konten kunci" in key:
                data["password"] = val

        if auth_list:
            data["authentication"] = ", ".join(auth_list)
        if cipher_list:
            data["cipher"] = ", ".join(cipher_list)

        return ProfileDetail(**data)
