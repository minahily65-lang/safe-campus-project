# Safe Campus Mobile

Android app wrapper around the Safe Campus web app (see the repo root for the
Flask + MongoDB backend), built with [Capacitor](https://capacitorjs.com/).
It loads the same web UI inside a native WebView shell, so backend and
frontend code are shared with the web version — only this wrapper is new.

## How it works

`capacitor.config.json` points the app at the Flask server's URL:

```json
"server": { "url": "http://<flask-server-ip>:5000", "cleartext": true }
```

- For the Android **emulator**, use `http://10.0.2.2:5000` (maps to the host
  machine's localhost).
- For a **real device**, use your PC's LAN IP (e.g. `http://192.168.1.23:5000`)
  and make sure the Flask app is started with `app.run(host="0.0.0.0", ...)`
  so it accepts connections from other devices on the network, and that
  Windows Firewall allows inbound TCP on port 5000.

After changing the URL, re-sync and rebuild:

```powershell
npx cap sync android
cd android
./gradlew assembleDebug
```

## Setup

Requires:
- Node.js
- JDK 21
- Android SDK (command-line tools, `platform-tools`, `platforms;android-34`,
  `build-tools;34.0.0`)

```powershell
npm install
npx cap sync android
```

Set `android/local.properties` (not committed) to point at your SDK:

```
sdk.dir=C:\\path\\to\\android-sdk
```

## Build

```powershell
cd android
./gradlew assembleDebug
```

Output APK: `android/app/build/outputs/apk/debug/app-debug.apk`

## Install on a device

1. Start the Flask backend (repo root) with `host="0.0.0.0"`.
2. Make sure the phone is on the same Wi-Fi network as the backend.
3. Sideload `app-debug.apk` onto the phone, or serve it over the LAN and
   download it from the phone's browser.
