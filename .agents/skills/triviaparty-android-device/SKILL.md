---
name: triviaparty-android-device
description: Use the project terminal and ADB to build/install Trivia Party on Android, transfer/import game ZIPs, and start local debug TV/player pages. Use when the user asks to install on the Pixel, update the app, install a package, or start debug aids.
---

# Trivia Party Android device workflow

Use PowerShell in the project terminal and ADB for Android device operations. Do not use Android Studio menus, phone mirroring, or computer UI automation to drive the IDE or phone unless the user specifically asks. Luna versus Sol does not determine whether terminal/ADB is available.

## Identify the operation

- An **APK** updates the Android app; install it with ADB. No mirroring is needed.
- A **game ZIP** is content, not an Android install package. Copy it to Downloads with ADB, then use Trivia Party's validated import flow on the phone. A successful push only confirms transfer, not import.
- **Debug TV/player pages** are served by the running host app on port 8080. ADB port forwarding plus a computer browser opens them; mirroring is unnecessary.

## Device and app install

From the project root, discover the Pixel and reuse its current serial. Do not ask the user to reconnect before checking:

```powershell
& H:/Android/Sdk/platform-tools/adb.exe devices -l
```

When source has changed, build the debug APK:

```powershell
.\gradlew.bat :app:assembleDebug --offline
```

Install and launch:

```powershell
& H:/Android/Sdk/platform-tools/adb.exe -s <serial> install -r --no-streaming app/build/outputs/apk/debug/app-debug.apk
& H:/Android/Sdk/platform-tools/adb.exe -s <serial> shell am start -n com.example.triviaparty/.MainActivity
```

Treat `Success` from `adb install` as confirmation. Check the APK path and timestamp if there is any doubt about which build is present. Never use `adb install` on a game ZIP.

## Game ZIP transfer and import

Transfer a package ZIP:

```powershell
& H:/Android/Sdk/platform-tools/adb.exe -s <serial> push <package.zip> /sdcard/Download/
```

On the phone, in Trivia Party choose **Outils → Importer un forfait**, then choose the ZIP in **Downloads**. If that package ID is already present, use package management → **Mettre à jour** before choosing it. The app importer validates the ZIP and extracts it into app-private storage. Do not report the package imported based only on `adb push`.

Use the phone itself for this app-only selection step; do not open Android Studio mirroring to perform it. Do not copy/unpack ZIP contents directly into the app's private package directory: that bypasses path, package, and question-count validation. If repeated unattended ZIP imports become necessary, implement a deliberate validated import interface instead of automating mirror taps.

## Debug TV and player

With the host game/server active on the Pixel, forward local port 18080 to the app's port 8080:

```powershell
& H:/Android/Sdk/platform-tools/adb.exe -s <serial> forward tcp:18080 tcp:8080
```

Open on the computer:

- `http://127.0.0.1:18080/tv` — debug TV/monitor
- `http://127.0.0.1:18080/play` — debug player

Reuse an existing mapping. Inspect forwards first if necessary:

```powershell
& H:/Android/Sdk/platform-tools/adb.exe forward --list
```

The app must have a running host game; forwarding alone does not start it. After app/asset changes, refresh the browser pages. The TV may require one click on **Activer le son** after reload because browsers restrict autoplay.

## ADB access and efficient reporting

If sandbox ADB fails because it cannot access the ADB home or wireless connection, request command approval/escalation and retry the ADB command in the approved context. Do not work around it with phone mirroring. Recheck `adb devices -l` and use the actual connected serial.

For public asset downloads, use the project terminal and save directly into the project's staging folder. The default sandbox may allow local terminal commands while blocking outbound DNS/network access; an error such as `No such host is known` from `Invoke-WebRequest` can indicate that sandbox restriction rather than a bad URL. When the user has authorized the downloads, retry the specific download command with elevated execution and a narrow justification describing the public source and workspace destination. Do not switch to browser/phone UI automation to work around terminal network restrictions. If elevated execution still cannot reach the source, report the exact network failure and continue with independent local work.

Keep these outcomes distinct when reporting: APK built, APK installed, ZIP transferred, ZIP imported in-app, host server active, and browser pages open. Prefer one discovery and direct ADB operations over IDE navigation. Do not run tests unless the user asks.
