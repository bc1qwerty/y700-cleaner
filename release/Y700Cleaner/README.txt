# Y700 Cleaner

Bloatware removal and performance optimization GUI for the Lenovo Legion Y700 tablet.

The tool auto-detects the device and shows a curated removal list tailored to the ROM.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Supported Devices

| Field | Lenovo Legion Y700 (Gen 4, 2025) |
|---|---|
| Codename | TB322FC |
| Firmware | ZUI ZUXOS 1.5.x (also tested on 1.1.11.x) |
| Android | 16 (API 35) |
| Platform | Qualcomm Snapdragon 8 Elite (sun) |
| Region | CN_OPEN (China domestic) |

> **Note**: The package list is built against the CN_OPEN ROM. Global ROMs may have different package names; any entries that aren't installed on the connected device are hidden automatically.

## Features

- Automatic device detection — connect via USB and the model is recognized instantly
- Bloatware grouped into categories with per-item selection, removal, and restore
- Live USB connection monitoring (3-second polling)
- Real-time action log
- Built-in protection for ZUI launcher/core, HyperEngine, Dolby, and Ready For (`KEEP_PACKAGES`)
- Performance tuning (animation scales, background scans, etc.)

## Removal Targets

- **Baidu / China trackers** — Baidu location tracking
- **Lenovo CN services** — Lenovo App Store, cloud sync, account (xbb), weather, Tianjiao education, privacy notice, floating menu assistant, screensaver
- **Lenovo telemetry** — Lenovo UX telemetry (`ue.device`, `ue.config`)
- **Lenovo push / ads** — "What's new" notifications, push ads, Xiaotian trigger
- **Lenovo voice / remote support** — Lenovo Voice, LeVision, LMSA
- **Factory / engineering test** — EngineeringCode, factory test, Lenovo auto-install config
- **ZUI optional apps** — ZUI Browser, AI Lens / Stylus, PP, xlog, Contacts, QR scanner, etc.
- **Android unnecessary apps** — print recommendations, HTML viewer, MMS, DeviceAsWebcam, emergency broadcast, etc.
- **Qualcomm XR / extras** — XR Wi-Fi / video, voice hotword
- **SIM / telephony** — eSIM, SIM-related services, LTE Broadcast Cell (Y700 is Wi-Fi only)
- **Ready For (PC mode unused)** — `com.motorola.mobiledesktop` and friends. Removed only if you don't use the PC monitor / Ready For workflow (avoids `leapp://` `ActivityNotFoundException` after `com.lenovo.leos.appstore` is removed)

## Protected Packages (Never Removed)

The following packages are declared in `KEEP_PACKAGES` and are excluded from the removal list.

| Category | Packages |
|---|---|
| Launcher / Core | `com.zui.launcher`, `com.zui.desktoplauncher`, `com.zui.cores`, `com.zui.engine`, `com.zui.resolver`, `com.zui.setupwizard` |
| Settings / UI | `com.zui.safecenter`, `com.zui.homesettings`, `com.zui.themes.provider`, `com.zui.dynamic.color.overlay` |
| Keyboard / Device | `com.zui.keyboardupdate.olympia`, `com.zui.deviceidservice` |
| Productivity | `com.zui.freeform.sidebar`, `com.zui.filemanager`, `com.zui.camera`, `com.zui.gallery` |
| Gaming | `com.lenovo.hyperengine`, `com.lenovo.tab_extreme`, `com.lenovo.tbengine` |
| Stylus / Split | `com.lenovo.penservice`, `com.lenovo.screensplit` |
| Media | `com.dolby.daxservice`, `com.dolby.dolbyvisionservice` |
| System Provider | `com.motorola.android.providers.settings` |
| **More-Connections deps** (v1.3, ANR-fix) | `com.qualcomm.qti.cne`, `com.android.printspooler`, `com.android.bips`, `vendor.qti.bluetooth.xpan`, `vendor.qti.data.ntnsatapp`, `com.qualcomm.qti.uceShimService`, `vendor.qti.imsrcs`, `vendor.qti.imsdatachannel`, `com.android.smspush`, `com.android.bluetoothmidiservice`, `com.android.hotspot2.osulogin`, `com.wapi.wapicertmanage` |

> **v1.3 note**: The Lenovo "More connections" settings page issues synchronous binder calls into a wide set of telephony / connectivity components. Removing any one of the items in the last row caused a 5-second ANR (`MoreConnectionsSettings`). They are now protected by `KEEP_PACKAGES`. If you previously removed them with v1.2, restore via `adb shell cmd package install-existing --user 0 <package>` or run a factory reset.

## Download

Grab the latest zip from the [Releases](../../releases) page.

No Python required — the exe and ADB binaries are bundled.

## Usage

### Prerequisite: Enable USB Debugging

1. Settings > About tablet > tap **Build number** seven times → "You are now a developer"
2. Settings > System > Developer options > enable **USB debugging**
3. Connect via USB → tap **Allow** on the "Allow USB debugging?" dialog

### Running the Program

1. Extract the zip
2. Connect the tablet via USB with USB debugging enabled
3. Launch `Y700Cleaner.exe` — the device is auto-detected
4. On the **Apps** tab, select packages and click **Remove Selected**
5. On the **Performance** tab, tick the settings you want and click **Apply Selected**

### Restoring

- Use the **Restore Selected** button inside the program
- A factory reset also restores everything automatically
- Manual: `adb shell cmd package install-existing <package>`

### CLI Mode

```
py y700_cleaner.py                  # Interactive mode
py y700_cleaner.py --list           # Print removal targets
py y700_cleaner.py --clean          # Run full removal
py y700_cleaner.py --restore        # Restore removed apps
py y700_cleaner.py --perf           # Apply default performance settings
py y700_cleaner.py --perf-reset     # Reset default performance settings
py y700_cleaner.py --perf-optional  # Walk through opt-in extras one by one
```

### Performance settings

The **Performance** tab is split into two sections:

- **Default settings** — animation scales, background scans, notification pop-ups, Play Protect verification, ADB install verification, stay-on-while-charging. The **Select All (default)** button only covers this section. These are safe for most users.
- **Opt-in extras** — Private DNS (AdGuard), haptic feedback off, ADB over Wi-Fi. These are **never included in Select All** and must be ticked individually, because they depend on personal preference or network setup.

The same split is enforced from the CLI: `--perf` applies the default section only, and `--perf-optional` walks through each extra individually and asks for `y/N`.

## Removal Method

```
adb shell pm uninstall -k --user 0 <package>
```

This operates at the user level and never touches the system partition. A factory reset restores every removed package automatically.

## Build (for developers)

```
py -m pip install customtkinter pyinstaller
py -m PyInstaller Y700Cleaner.spec --clean --noconfirm
```

This produces `dist/Y700Cleaner.exe`.

## Folder Layout

```
Y700Cleaner/
├── Y700Cleaner.exe          # GUI executable
├── platform-tools/          # Bundled ADB
│   ├── adb.exe
│   ├── AdbWinApi.dll
│   └── AdbWinUsbApi.dll
└── README.txt               # Quick reference
```

## Safety Principles

This project carries over the lessons learned from the `boox-cleaner` v2.2 incident (removing `com.onyx.kreader` caused `ContentBrowser` to crash on boot due to a `ContentProvider` dependency).

- Every action runs at the user level (`--user 0`)
- Launcher / core / keyboard / gaming engine / connectivity components / system providers are guarded by `KEEP_PACKAGES`
- Packages of unknown purpose are intentionally left out of the default removal list
- Every change reverts automatically on factory reset

## License

MIT
