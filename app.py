import os
import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB max upload size

# Ensure upload directories exist on startup
os.makedirs(config.ROM_FOLDER, exist_ok=True)
os.makedirs(config.COVER_FOLDER, exist_ok=True)

# In-memory state for second-screen TV Mode synchronization
now_playing = {"game": None}


def get_db():
    """Return a SQLite connection with dictionary-like row access."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Automatically create the games table if it does not exist."""
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                console TEXT NOT NULL,
                core TEXT NOT NULL,
                rom_filename TEXT NOT NULL,
                cover_filename TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def allowed_file(filename, allowed_set):
    """Verify file has a valid, whitelisted extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set


# Initialize database automatically when app starts
init_db()


@app.route("/")
def index():
    """Mobile/tablet/desktop main library & remote controller view."""
    selected_console = request.args.get("console", "").strip()
    search_query = request.args.get("q", "").strip()

    query = "SELECT * FROM games WHERE 1=1"
    params = []

    if selected_console:
        query += " AND console = ?"
        params.append(selected_console)

    if search_query:
        query += " AND title LIKE ?"
        params.append(f"%{search_query}%")

    query += " ORDER BY title ASC"

    with get_db() as conn:
        games = conn.execute(query, params).fetchall()
        db_consoles = [row["console"] for row in conn.execute("SELECT DISTINCT console FROM games").fetchall()]

    all_consoles = sorted(set(list(config.SUPPORTED_CONSOLES.keys()) + db_consoles))

    return render_template(
        "index.html",
        games=games,
        consoles=all_consoles,
        selected_console=selected_console,
        search_query=search_query,
        cast_app_id=config.CAST_APP_ID,
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Form to add a new ROM and optional cover image."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        console = request.form.get("console", "").strip()
        custom_console = request.form.get("custom_console", "").strip()
        custom_core = request.form.get("custom_core", "").strip().lower()
        rom_file = request.files.get("rom_file")
        cover_file = request.files.get("cover_file")

        # Validate game title
        if not title:
            flash("Please provide a game title.", "error")
            return redirect(url_for("upload"))

        # Determine console name and EmulatorJS core (built-in or custom)
        if console == "custom":
            if not custom_console or not custom_core:
                flash("Please enter both a custom console name and an EmulatorJS core ID.", "error")
                return redirect(url_for("upload"))
            final_console = custom_console
            core = custom_core
        elif console in config.SUPPORTED_CONSOLES:
            final_console = console
            core = config.SUPPORTED_CONSOLES[console]
        else:
            flash("Please select a valid console.", "error")
            return redirect(url_for("upload"))

        # Validate ROM file
        if not rom_file or rom_file.filename == "":
            flash("Please choose a valid ROM file to upload.", "error")
            return redirect(url_for("upload"))

        if not allowed_file(rom_file.filename, config.ALLOWED_ROM_EXTENSIONS):
            flash("Unsupported ROM file type.", "error")
            return redirect(url_for("upload"))

        # Save ROM safely
        rom_filename = secure_filename(rom_file.filename)
        rom_file.save(os.path.join(config.ROM_FOLDER, rom_filename))

        # Save optional cover image
        cover_filename = None
        if cover_file and cover_file.filename != "":
            if allowed_file(cover_file.filename, config.ALLOWED_IMAGE_EXTENSIONS):
                cover_filename = secure_filename(cover_file.filename)
                cover_file.save(os.path.join(config.COVER_FOLDER, cover_filename))

        # Insert record into SQLite
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO games (title, console, core, rom_filename, cover_filename)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, final_console, core, rom_filename, cover_filename),
            )
            conn.commit()

        flash(f"Added '{title}' ({final_console}) to your library!", "success")
        return redirect(url_for("index"))

    return render_template("upload.html", consoles=list(config.SUPPORTED_CONSOLES.keys()))


@app.route("/delete/<int:game_id>", methods=["POST"])
def delete_game(game_id):
    """Delete a game from SQLite and remove its ROM and cover files from disk."""
    with get_db() as conn:
        game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
        if not game:
            flash("Game not found.", "error")
            return redirect(url_for("index"))

        # Remove the ROM file from static/roms/ if it exists
        if game["rom_filename"]:
            rom_path = os.path.join(config.ROM_FOLDER, game["rom_filename"])
            if os.path.exists(rom_path):
                os.remove(rom_path)

        # Remove the cover image from static/covers/ if it exists
        if game["cover_filename"]:
            cover_path = os.path.join(config.COVER_FOLDER, game["cover_filename"])
            if os.path.exists(cover_path):
                os.remove(cover_path)

        # Remove the database record
        conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()

    # Clear TV Mode now_playing if the deleted game was active
    if now_playing.get("game") and now_playing["game"].get("id") == game_id:
        now_playing["game"] = None

    flash(f"Removed '{game['title']}' from your library.", "success")
    return redirect(url_for("index"))


@app.route("/play/<int:game_id>")
def play(game_id):
    """Browser-based EmulatorJS screen supporting touch, keyboard, and gamepads."""
    with get_db() as conn:
        game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()

    if not game:
        flash("Game not found.", "error")
        return redirect(url_for("index"))

    return render_template("play.html", game=game, cast_app_id=config.CAST_APP_ID)


@app.route("/receiver")
def receiver():
    """Chromecast / Smart TV / Secondary-monitor display receiver."""
    return render_template("receiver.html")


@app.route("/api/now-playing", methods=["GET", "POST"])
def api_now_playing():
    """Sync active game selection between controller devices and TV Mode."""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        game_id = data.get("game_id")

        with get_db() as conn:
            game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()

        if not game:
            return jsonify({"status": "error", "message": "Game not found"}), 404

        now_playing["game"] = {
            "id": game["id"],
            "title": game["title"],
            "console": game["console"],
            "core": game["core"],
            "rom_url": url_for("static", filename=f"roms/{game['rom_filename']}"),
            "cover_url": url_for("static", filename=f"covers/{game['cover_filename']}") if game["cover_filename"] else None,
            "play_url": url_for("play", game_id=game["id"]),
        }
        return jsonify({"status": "ok", "game": now_playing["game"]})

    return jsonify(now_playing)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
