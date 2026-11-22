const CAST_NAMESPACE = "urn:x-cast:com.retrogameshub.cast";
const STORAGE_KEY = "retrogameshub_cast_app_id";
const DEFAULT_PUBLIC_CAST_ID = "CC1AD845";

function getActiveCastAppId() {
    const savedId = localStorage.getItem(STORAGE_KEY);
    if (savedId && savedId.trim() !== "") {
        return savedId.trim();
    }
    if (window.CAST_APP_ID && window.CAST_APP_ID !== "YOUR_CAST_APP_ID") {
        return window.CAST_APP_ID;
    }
    return DEFAULT_PUBLIC_CAST_ID;
}

// Initialize Google Cast SDK when Chrome loads it
window["__onGCastApiAvailable"] = function (isAvailable) {
    if (!isAvailable) return;
    try {
        cast.framework.CastContext.getInstance().setOptions({
            receiverApplicationId: getActiveCastAppId(),
            autoJoinPolicy: chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED,
        });
    } catch (err) {
        console.warn("Google Cast initialization notice:", err);
    }
};

// Sync with Flask TV Mode and trigger Chromecast device picker
async function castGame(gameId) {
    try {
        const response = await fetch("/api/now-playing", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: gameId }),
        });
        const data = await response.json();

        // Check if Google Cast SDK is fully initialized
        const castReady = Boolean(
            window.cast &&
            cast.framework &&
            cast.framework.CastContext
        );

        if (castReady) {
            const context = cast.framework.CastContext.getInstance();
            let session = context.getCurrentSession();

            if (!session) {
                await context.requestSession();
                session = context.getCurrentSession();
            }

            if (session && data.game) {
                await session.sendMessage(CAST_NAMESPACE, {
                    action: "LOAD_GAME",
                    game: data.game,
                });
            }
            return;
        }

        // Fallback if Google Cast SDK isn't ready yet: open TV Mode tab directly
        window.open("/receiver", "_blank");
    } catch (err) {
        if (err !== "cancel" && err?.code !== "cancel") {
            console.warn("Cast session notice:", err);
            window.open("/receiver", "_blank");
        }
    }
}

// Wire up all buttons once the page finishes loading
document.addEventListener("DOMContentLoaded", () => {
    const setIdBtn = document.getElementById("set-cast-id-btn");
    const castHelpBtn = document.getElementById("cast-help-btn");
    const castModal = document.getElementById("cast-modal");
    const closeCastModal = document.getElementById("close-cast-modal");

    if (castHelpBtn && castModal) {
        castHelpBtn.addEventListener("click", () => castModal.showModal());
    }

    if (closeCastModal && castModal) {
        closeCastModal.addEventListener("click", () => castModal.close());
    }

    if (setIdBtn) {
        setIdBtn.addEventListener("click", () => {
            const current = localStorage.getItem(STORAGE_KEY) || "";
            const input = prompt(
                "Enter a Custom Google Cast Receiver App ID (leave blank for default):",
                current
            );
            if (input === null) return;

            if (input.trim() === "") {
                localStorage.removeItem(STORAGE_KEY);
                alert("Reset to default public Cast receiver. Reloading...");
            } else {
                localStorage.setItem(STORAGE_KEY, input.trim());
                alert(`Saved Custom Cast App ID: ${input.trim()}. Reloading...`);
            }
            window.location.reload();
        });
    }

    // Use event delegation on document so every ".btn-cast" works immediately
    document.addEventListener("click", (event) => {
        const btn = event.target.closest(".btn-cast");
        if (!btn) return;
        const gameId = parseInt(btn.dataset.gameId, 10);
        if (!Number.isNaN(gameId)) {
            castGame(gameId);
        }
    });
});

