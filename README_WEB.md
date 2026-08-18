# Safe Campus Web — Mobile UI Version

## Start

Open PowerShell in the inner `Safe Campus Web` folder and run:

```powershell
python main.py
```

Then open:

`http://127.0.0.1:5000/`

## Startup flow

Splash Screen -> Login -> role-based dashboard.

## Mobile preview

On desktop, the app is shown in a 390 x 844 phone-style frame. On a real phone or a narrow browser, it expands to the full viewport.

## New logo

The new shield + bell logo is stored as:

`static/assets/safe-campus-logo.png`

and is used throughout the app.

## SOS alarm

Security staff must click **Enable SOS Alarm** once because browsers block background audio until the page has received a user interaction. After that, the security dashboard polls for new pending SOS alerts every 3 seconds and plays `alarm.mp3` when a new alert arrives.
