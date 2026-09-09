# xntsh

minimal textual tui toolkit to inspect saved wi-fi profiles, monitor active network interfaces, scan nearby access points, and run diagnostics on windows.

built on top of `netsh`, structured with screen-based navigation, modal dialogs, and decoupled styling.

## features

- main menu navigation: arrow keys, enter, or quick number keys (1-4) to switch modules.
- saved profiles manager:
  - list all saved wi-fi networks with pagination.
  - instant search filter.
  - view cleartext password and full profile parameters in modal dialog.
  - delete/forget network with confirmation modal.
  - export profile to xml with key=clear.
- live network & scanner:
  - active interface card (ssid, signal %, channel, band, rx/tx rate).
  - nearby wi-fi scan table with bssid, signal %, and security type.
- hardware & ip diagnostics:
  - wi-fi driver details and hardware capabilities.
  - ipv4 address, subnet, gateway, and dns server configurations.
- error handling: clean notification popups, zero raw tracebacks leaked.

## requirements

- windows 10 / 11
- python 3.10+
- dependencies in `requirements.txt`

## installation

```bash
git clone https://github.com/vscple/xntsh.git
cd xntsh
pip install -r requirements.txt
```

## usage

```bash
python main.py
```

## keybindings

### main menu

| key | action |
| --- | --- |
| `up` / `down` | navigate menu options |
| `enter` | select highlighted option |
| `1` | open saved profiles manager |
| `2` | open live network & nearby scanner |
| `3` | open hardware & ip diagnostics |
| `4` / `ctrl+c` | quit application |

### sub-screens (common)

| key | action |
| --- | --- |
| `esc` / `b` | back to main menu |
| `r` | refresh / rescan data |
| `ctrl+c` | quit application |

### saved profiles manager

| key | action |
| --- | --- |
| `enter` / click | view cleartext password & full profile modal |
| `d` | delete / forget selected wi-fi profile |
| `e` | export selected profile to xml |
| `/` | focus search bar |
| `left` / `right` | previous / next page |

## project structure

- `services.py`: subprocess wrapper around `netsh` commands.
- `widgets.py`: reusable ui components (modals, search bar, pagination).
- `screens.py`: modular screens (main menu, profiles, live network, diagnostics).
- `styles.tcss`: decoupled textual stylesheet.
- `app.py`: application router and screen stack manager.
- `main.py`: application entry point.
- `tests/`: test suite verifying parsers and screen transitions.

## testing

```bash
python tests/test_services.py
python tests/test_app.py
```
