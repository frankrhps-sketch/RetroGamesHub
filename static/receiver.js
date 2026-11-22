const CAST_NAMESPACE = "urn:x-cast:com.RetroGamesHub.cast";
let currentGameId = null;

function renderGameOnTV(game) {
    const idleBox = document.getElementById("tv-idle");
    const activeBox = document.getElementById("tv-active");

    if (!game) {
        idleBox.style.display = "block";
        activeBox.style.display = "none";
        currentGameId = null;
        return;
    }

    if (currentGameId === game.id) return;
    currentGameId = game.id;

    idleBox.style.display = "none";
    activeBox.style.display = "block";

    document.getElementById("tv-title").textContent = game.title;
    document.getElementById("tv-console").textContent = game.console;
    document.getElementById("tv-launch-btn").href = `/play/${game.id}`;

    const coverBox = document.getElementById("tv-cover");
    if (game.cover_filename) {
        coverBox.innerHTML =
            `<img src="/static/covers/${game.cover_filename}" alt="${game.title}" style="width: 100%; display: block;">`;
    } else {
        coverBox.innerHTML =
            `<div class="cover-placeholder" style="height: 240px; display: flex; align-items: center; justify-content: center; background: #1e293b; font-size: 1.5rem;">${game.console}</div>`;
    }
}

// 1. Start Google Cast Receiver Context if running on a Chromecast
try {
    if (window.cast && cast.framework) {
        const context = cast.framework.CastReceiverContext.getInstance();
        context.addCustomMessageListener(CAST_NAMESPACE, (event) => {
            if (event.data && event.data.game) {
                renderGameOnTV(event.data.game);
            }
        });
        context.start();
    }
} catch (err) {
    console.log("Running in standard TV browser mode.");
}

// 2. Poll Flask API every 2 seconds so Smart TV browsers & second screens stay synced
setInterval(async () => {
    try {
        const res = await fetch("/api/now-playing");
        const data = await res.json();
        if (data.game) {
            renderGameOnTV(data.game);
        }
    } catch (err) {
        // Ignore transient network hiccups
    }
}, 2000);
