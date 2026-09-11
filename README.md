# xntsh

minimal textual tui toolkit to inspect saved wi-fi profiles, monitor active network interfaces, scan nearby access points, run speed tests, and view diagnostics on windows.

built on top of `netsh` and native python stdlib, structured with screen-based navigation, modal dialogs, and decoupled styling.

## features

- main menu navigation: arrow keys, enter, or quick number keys (1-5) to switch modules.
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
- speedtest:
  - native download, upload, and ping measurement using https edge endpoints.
  - zero external dependencies (pure stdlib).
  - summary table: latest, highest, lowest, and average across session runs.
  - full history table with timestamp, speed values, and server used.
  - non-blocking async execution with loading indicator.
- error handling: clean notification popups, zero raw tracebacks leaked.

## requirements

- windows 10 / 11
- python 3.10+
- dependencies in `requirements.txt`

## installation

```bash
git clone https://github.com/Marvellbrazil/xntsh.git
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
| `4` | open speedtest |
| `5` / `ctrl+c` | quit application |

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

### speedtest

| key | action |
| --- | --- |
| `enter` | start or re-run speedtest |
| `r` | re-run speedtest |

## project structure

- `services.py`: subprocess wrapper around `netsh` commands and speedtest runner.
- `widgets.py`: reusable ui components (modals, search bar, pagination).
- `screens.py`: modular screens (main menu, profiles, live network, diagnostics, speedtest).
- `styles.tcss`: decoupled textual stylesheet.
- `app.py`: application router and screen stack manager.
- `main.py`: application entry point.
- `tests/`: test suite verifying parsers, summary calculations, and screen transitions.

## testing

```bash
python tests/test_services.py
python tests/test_app.py
```
