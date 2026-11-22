# RetroGamesHub
#### Video Demo: https://youtu.be
#### GitHub: frankrhps-sketch
#### Description:


**RetroGamesHub** is a portable, browser-based retro gaming library and emulation hub built with Python, Flask, SQLite, HTML/CSS, and JavaScript. Designed to be accessible to everyday, non-technical users while remaining extensible for developers, the application lets anyone upload legally owned or homebrew ROM files across 16+ classic consoles (or specify any custom Libretro/EmulatorJS core), play directly in any mobile, tablet, or desktop web browser, and cast or sync their session to a television or secondary screen.

---

## Key Features

- **Cross-Device Responsive Library:** Built with a mobile-first CSS grid and touch-friendly tap targets (`42px+`), adapting seamlessly from smartphones and tablets to desktop monitors and widescreen TVs.
- **Expanded Console Support & Custom Platform Input:** Supports 16 built-in retro systems out of the box—including **NES, SNES, Nintendo 64, Game Boy / Color, Game Boy Advance, Nintendo DS, Sega Genesis / Mega Drive, Sega Master System, Sega Game Gear, Sega 32X, PlayStation 1, Atari 2600, Atari 7800, PC Engine / TurboGrafx-16, Neo Geo Pocket, and Arcade**—plus an **Other / Custom Console** option on the upload form that lets users input any custom platform name and EmulatorJS core ID without editing code.
- **In-Browser ROM Uploader & Dynamic Catalog:** Users can upload ROM files (`.nes`, `.smc`, `.sfc`, `.n64`, `.z64`, `.v64`, `.gb`, `.gbc`, `.gba`, `.nds`, `.md`, `.gen`, `.sms`, `.gg`, `.32x`, `.bin`, `.cue`, `.iso`, `.chd`, `.pbp`, `.a26`, `.a78`, `.pce`, `.ngp`, `.ngc`, `.zip`) along with optional cover art via `/upload`, search titles, and filter dynamically by console.
- **Zero-Install Emulation with Multi-Input Support:** Powered by **EmulatorJS**, games run directly in the browser with automatic on-screen touch controls on mobile devices, keyboard/mouse mapping on desktops, and plug-and-play USB or Bluetooth gamepad support via the HTML5 Gamepad API.
- **Dual-Mode TV Casting (Consumer + Developer Options):**
  - **Everyday User Mode:** Includes an in-app **📺 Cast to TV** guide modal supporting standard browser tab casting (Chromecast/Google TV) as well as a built-in **TV Mode (`/receiver`)** that syncs live over Wi-Fi with any Smart TV, console, or second-monitor browser.
  - **Developer Mode:** Supports custom Google Cast Web Receiver Application IDs via `config.py`, environment variables, or an in-browser `localStorage` configurator (`⚙️ Developer Cast ID`) inside the Cast modal.
- **Portable Auto-Setup:** Automatically creates the SQLite database (`games.db`) and required upload folders on first launch so anyone can download and run the application immediately.
---

## Project Structure


```text
project/
├── app.py                  # Main Flask application, routes, custom console handler, and JSON sync API
├── config.py               # Centralized settings for paths, allowed extensions, 16 console cores, and Cast IDs
├── requirements.txt        # Python package dependencies (Flask, Werkzeug)
├── README.md               # Project documentation, setup instructions, and attributions
├── .gitignore              # Excludes local databases, EmulatorJS binaries, and user-uploaded ROMs
├── static/
│   ├── styles.css          # Responsive dark-themed styling for mobile, tablet, desktop, and TV screens
│   ├── sender.js           # Client-side casting logic, Cast Help modal controller, and localStorage ID manager
│   ├── receiver.js         # TV display listener supporting both Google Cast SDK messages and Flask API polling
│   ├── gamepad.js          # HTML5 Gamepad API script enabling USB/Bluetooth controller navigation on the menu
│   ├── covers/             # Directory storing uploaded game box art
│   ├── roms/               # Directory storing uploaded ROM files
│   └── emulatorjs/         # Local copy of EmulatorJS assets (downloaded during setup)
└── templates/
    ├── layout.html         # Base Jinja template with responsive viewport, navbar, and Cast guide dialog
    ├── index.html          # Main game library grid with search bar, dynamic console filter, Play, and Cast buttons
    ├── upload.html         # Form interface for uploading ROMs, cover art, or custom console/core pairs
    ├── play.html           # Fullscreen EmulatorJS player configured dynamically per console core
    └── receiver.html       # Clutter-free widescreen TV display for Chromecast and second-screen browsers

---

## File-by-File Breakdown

- **`config.py`:** Separates configuration from application logic using relative `os.path` directories so the project runs identically on Windows, macOS, and Linux. Defines `ALLOWED_ROM_EXTENSIONS` across 26 file formats and maps 16 human-readable console names to their corresponding EmulatorJS core identifiers.
- **`app.py`:** Initializes the Flask server and automatically executes `init_db()` on startup to create the `games` table in SQLite if it does not exist. Handles four primary web routes (`/`, `/upload`, `/play/<int:game_id>`, `/receiver`) and a JSON endpoint (`/api/now-playing`) that tracks the active game for TV Mode synchronization. Dynamically merges `config.SUPPORTED_CONSOLES` with custom console names stored in `games.db`.
- **`templates/layout.html`:** Provides the shared HTML5 shell, inline SVG emoji favicon, sticky navigation bar, flash message alerts, and an interactive `<dialog>` modal explaining how to cast to a TV alongside optional developer Cast ID settings.
- **`templates/index.html`:** Renders the searchable, filterable card grid of uploaded games. Attaches `data-game-id` attributes to Cast buttons so JavaScript can trigger casting cleanly without inline template expressions.
- **`templates/upload.html`:** Provides a multipart file upload form allowing users to select from 16 built-in consoles or choose **Other / Custom Console...** to dynamically reveal fields for a custom platform name and EmulatorJS core ID.
- **`templates/play.html`:** Configures global `EJS_*` variables (`EJS_core`, `EJS_gameUrl`, `EJS_pathtodata`, `EJS_threads = false`) and loads EmulatorJS locally from `static/emulatorjs/data/loader.js` for reliable, offline-capable gameplay.
- **`templates/receiver.html`:** A minimal widescreen interface designed for televisions. Displays an idle prompt until a game is pushed from the controller screen, then reveals the selected game's box art, console badge, and launch button.
- **`static/styles.css`:** Implements CSS custom properties (`--bg`, `--surface`, `--primary`, `--accent`), responsive CSS Grid auto-fill cards, and mobile breakpoints (`@media (max-width: 480px)`).
- **`static/sender.js`:** Manages the Cast guide modal, stores optional user-entered Google Cast App IDs in `localStorage` (`retrogameshub_cast_app_id`), sends POST requests to `/api/now-playing`, and transmits custom namespace messages (`urn:x-cast:com.retrogameshub.cast`) when a Chromecast session is active.
- **`static/receiver.js`:** Listens for incoming custom messages via `cast.framework.CastReceiverContext` when running on a Chromecast, while simultaneously polling `/api/now-playing` every 2 seconds so standard Smart TV or second-monitor browsers stay synchronized without requiring a Google Developer account.
- **`static/gamepad.js`:** Uses `navigator.getGamepads()` and `requestAnimationFrame` to let users browse game cards left/right with a physical USB or Bluetooth controller D-pad/analog stick and launch the focused game with the primary action button.

---

## Design Choices & Technical Trade-Offs

1. **Local EmulatorJS Hosting vs. External CDNs:** Initially, EmulatorJS was loaded via external CDNs (`cdn.emulatorjs.org` and `cdn.jsdelivr.net`). However, DNS/network timeouts and strict browser cross-origin isolation rules (`SharedArrayBuffer`) caused intermittent black screens. Hosting EmulatorJS locally under `static/emulatorjs/` with `EJS_threads = false` eliminated network timeouts and made the entire gaming environment self-contained and offline-ready.
2. **Extensible Console Architecture:** Rather than hard-coding a fixed list of consoles into HTML or SQL constraints, storing both the display `console` name and the EmulatorJS `core` string in SQLite allows users to add unsupported or niche platforms (such as PSP, Sega Saturn, or ColecoVision) directly from the UI without modifying backend code.
3. **Dual-Mode Casting Architecture:** Relying exclusively on the Google Cast Custom Web Receiver SDK would prevent users without a paid Google Cast Developer account—or users running the app in local/sandboxed environments like GitHub Codespaces—from casting. Combining the official Google Cast SDK with a built-in `/receiver` polling endpoint and Chrome tab-casting instructions ensures that *any* user can cast to a TV out of the box while preserving native Cast SDK functionality for developers.
4. **Database & Asset Portability:** Rather than requiring manual SQL schema imports or hard-coded local paths, `app.py` auto-creates `games.db` and upload directories at runtime. Commercial ROMs and third-party emulator binaries are excluded via `.gitignore` so the repository stays lightweight and compliant with copyright and CS50 academic honesty guidelines.

---

## Installation & Setup (Running Locally)

1. **Clone or download the project folder** and navigate into it:
   ```bash
   cd project
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Download EmulatorJS assets** into `static/emulatorjs/`:
   ```bash
   URL="https://github.com""/EmulatorJS/EmulatorJS/archive/refs/heads/main.zip"
   curl -L -o emulatorjs.zip "\$URL"
   unzip -q emulatorjs.zip
   mv EmulatorJS-main static/emulatorjs
   rm emulatorjs.zip
   ```
4. **Start the Flask server:**
   ```bash
   python app.py
   ```
5. **Open the application:** Visit `http://127.0.0.1:5000` in your browser, click **+ Add ROM** to upload a free homebrew or legally owned ROM (such as `2048.nes`), and click **▶ Play** or **📡 Cast**.

## Credits & Attributions

- **EmulatorJS:** Open-source browser-based RetroArch/Libretro emulation wrapper (EmulatorJS on GitHub).
- **Google Cast Web Sender & Receiver SDKs:** Used for optional custom Chromecast integration (Google Cast Developers).
- **Flask & Werkzeug:** Python web framework and secure file upload utilities.
- **Homebrew Testing ROM:** Tested using open-source NES homebrew *2048* (retrobrews/nes-games on GitHub).
