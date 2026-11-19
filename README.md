# Always On Top for Flow Launcher

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Flow Launcher](https://img.shields.io/badge/Flow%20Launcher-Plugin-blue)](https://www.flowlauncher.com/)

Pin any **taskbar window** to stay always on top — similar to [PowerToys Always On Top](https://learn.microsoft.com/windows/powertoys/always-on-top), right inside Flow Launcher.

**Keyword:** `aot`

---

## Features

| Feature | Description |
|---------|-------------|
| Taskbar windows only | Lists only windows that appear on the Windows taskbar |
| Pin / Unpin | Click a window to toggle always-on-top |
| Unpin all | First result is always **取消置顶** — clears all pinned windows in one action |
| Live status | Pinned windows show 📌; list refreshes after each action |
| Search filter | Type `aot chrome` to filter by title |
| Safe Win32 API | Only `SetWindowPos` (z-order). No hooks, no injection, no focus steal |

---

## Demo usage

1. Open Flow Launcher
2. Type `aot`
3. First item **取消置顶** — unpin everything currently pinned
4. Pick any listed window — pin or unpin it
5. Optional: `aot notepad` to filter titles containing “notepad”

---

## Install

### From Plugin Store (after published)

```
pm install Always On Top
```

Or: **Settings → Plugins → Plugin Store → search “Always On Top”**

### Manual install

1. Download the latest `Flow.Launcher.Plugin.AlwaysOnTop.zip` from [Releases](../../releases)
2. Extract the zip into:

```
%APPDATA%\FlowLauncher\Plugins\
```

3. Fully exit Flow Launcher (tray → Exit) and open it again
4. Type `aot`

### Python dependency

This plugin needs the `flowlauncher` package in the Python that Flow uses.

If you see `No module named 'flowlauncher'`:

```powershell
# Replace with the Python path shown in Flow settings (Python Path)
"C:\Path\To\Your\python.exe" -m pip install flowlauncher
```

Official releases built by GitHub Actions also vendor `flowlauncher` into a `lib/` folder so most users do not need a manual pip install.

---

## Requirements

- Windows 10 / 11
- [Flow Launcher](https://www.flowlauncher.com/) 1.9+ (2.x recommended)
- Python 3.8+ configured in Flow Launcher (Settings → Python Path)

---

## How it works (safety)

- Enumerates top-level windows with `EnumWindows`
- Filters to **taskbar-style** windows (visible, titled, not tool windows, not shell classes)
- Pin/unpin via `SetWindowPos(HWND_TOPMOST / HWND_NOTOPMOST)` with:
  - `SWP_NOMOVE` — does not move the window
  - `SWP_NOSIZE` — does not resize
  - `SWP_NOACTIVATE` — does not steal focus
- No global hooks, no process injection, no elevated privileges required
- Elevated (admin) windows may refuse the call under UIPI if Flow is not elevated — that is normal Windows behavior

---

## Development

```text
Flow.Launcher.Plugin.AlwaysOnTop/
├── plugin.json          # Flow manifest
├── main.py              # Plugin entry
├── requirements.txt     # flowlauncher
├── Images/app.png       # Icon
├── LICENSE
├── README.md
└── .github/workflows/PublishRelease.yml
```

Local test:

1. Copy the folder to `%APPDATA%\FlowLauncher\Plugins\`
2. `pip install flowlauncher` into Flow’s Python
3. Restart Flow, type `aot`

Release:

1. Bump `"Version"` in `plugin.json`
2. Push a tag `v1.1.2` (or run the workflow manually)
3. GitHub Actions builds the zip (with `lib/`) and creates a Release

---

## Publish checklist (Flow Plugin Store)

See [PUBLISH.md](PUBLISH.md) for the full step-by-step guide.

Summary:

1. Put this repo on GitHub (public)
2. Create a Release via the Actions workflow (zip attached)
3. Fork [Flow.Launcher.PluginsManifest](https://github.com/Flow-Launcher/Flow.Launcher.PluginsManifest)
4. Add `plugins/AlwaysOnTop-<ID>.json` and open a PR
5. After merge, wait for CDN sync (can take hours to a few days)
6. Users can `pm install Always On Top`

---

## Changelog

### 1.1.2

- Harden HWND checks (`IsWindow`) and exception handling
- Refuse system shell window classes
- Safer pin path (taskbar filter before enable)

### 1.1.1

- Refresh list after pin/unpin (`dontHideAfterAction` + `ChangeQuery`)
- Status text and 📌 update immediately

### 1.1.0

- Only taskbar windows
- First result always “取消置顶”

### 1.0.0

- Initial release

---

## License

MIT — see [LICENSE](LICENSE)

---

## Credits

- [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher)
- Inspired by [PowerToys Always On Top](https://learn.microsoft.com/windows/powertoys/always-on-top)
