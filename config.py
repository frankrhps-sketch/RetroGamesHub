import os

# Base directory of the project (keeps paths portable on Windows, Mac, and Linux)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Folders for user-uploaded ROMs and cover art
ROM_FOLDER = os.path.join(BASE_DIR, "static", "roms")
COVER_FOLDER = os.path.join(BASE_DIR, "static", "covers")
DATABASE_PATH = os.path.join(BASE_DIR, "games.db")

# Allowed file extensions for uploads
ALLOWED_ROM_EXTENSIONS = {
    "nes", "smc", "sfc", "n64", "z64", "v64",
    "gb", "gbc", "gba", "nds",
    "md", "gen", "sms", "gg", "32x",
    "bin", "cue", "iso", "chd", "pbp",
    "a26", "a78", "pce", "ngp", "ngc", "zip"
}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# Maps console names to EmulatorJS core identifiers
SUPPORTED_CONSOLES = {
    "NES": "nes",
    "SNES": "snes",
    "Nintendo 64": "n64",
    "Game Boy / Color": "gb",
    "Game Boy Advance": "gba",
    "Nintendo DS": "nds",
    "Sega Genesis / Mega Drive": "segaMD",
    "Sega Master System": "segaMS",
    "Sega Game Gear": "segaGG",
    "Sega 32X": "sega32x",
    "PlayStation 1": "psx",
    "Atari 2600": "atari2600",
    "Atari 7800": "atari7800",
    "PC Engine / TurboGrafx-16": "pce",
    "Neo Geo Pocket": "ngp",
    "Arcade (MAME / FBNeo)": "arcade",
}

# Optional Google Cast App ID (users can override via environment variable or edit here)
CAST_APP_ID = os.environ.get("CAST_APP_ID", "CC1AD845")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-retro-games-hub-secret-key")
