# xntsh

minimal textual tui to inspect saved wi-fi profiles and passwords on windows.

built on top of `netsh wlan`, structured with modular separation, input validation, and modal inspection.

## features

- profile discovery: automatically queries and lists saved wlan profiles.
- live search: filter ssids instantly by typing.
- pagination: fixed row paging with previous/next controls.
- modal inspection: press enter on any profile to view cleartext keys and network parameters.
- safe error handling: silent failover with notifications, zero raw tracebacks leaked.

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

| key | action |
| --- | --- |
| `enter` / click | open modal with cleartext password and profile data |
| `/` | focus search input |
| `left` | previous page |
| `right` | next page |
| `r` | refresh profile list |
| `esc` / `ctrl+c` | close modal |
| `ctrl+c` | quit app |

## project structure

- `services.py`: subprocess wrapper around `netsh` without shell execution.
- `widgets.py`: textual components (search bar, pagination, table, detail modal).
- `styles.tcss`: decoupled textual stylesheet.
- `app.py`: application controller, state management, and notification handling.
- `main.py`: application entry point.
- `tests/`: test suite verifying parsers and headless tui flows.

## testing

```bash
python tests/test_services.py
python tests/test_app.py
```
