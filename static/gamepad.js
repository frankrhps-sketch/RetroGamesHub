// Allows navigating game cards on the home screen with a Bluetooth or USB controller
let focusedIndex = 0;
let lastMoveTime = 0;

function pollGamepadMenu() {
    const cards = Array.from(document.querySelectorAll(".game-card"));
    if (cards.length === 0) {
        requestAnimationFrame(pollGamepadMenu);
        return;
    }

    const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
    const pad = gamepads[0];
    const now = Date.now();

    if (pad && now - lastMoveTime > 200) {
        const axisX = pad.axes[0] || 0;
        const dpadLeft = pad.buttons[14] && pad.buttons[14].pressed;
        const dpadRight = pad.buttons[15] && pad.buttons[15].pressed;
        const buttonA = pad.buttons[0] && pad.buttons[0].pressed;

        if (axisX > 0.5 || dpadRight) {
            focusedIndex = (focusedIndex + 1) % cards.length;
            cards[focusedIndex].focus();
            lastMoveTime = now;
        } else if (axisX < -0.5 || dpadLeft) {
            focusedIndex = (focusedIndex - 1 + cards.length) % cards.length;
            cards[focusedIndex].focus();
            lastMoveTime = now;
        } else if (buttonA && document.activeElement && document.activeElement.classList.contains(
                "game-card")) {
            const playLink = document.activeElement.querySelector(".btn-play");
            if (playLink) playLink.click();
            lastMoveTime = now;
        }
    }

    requestAnimationFrame(pollGamepadMenu);
}

window.addEventListener("gamepadconnected", () => {
    console.log("Gamepad connected for menu navigation!");
    requestAnimationFrame(pollGamepadMenu);
});
