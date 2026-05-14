const socket_pain = window.socket;

const DWELL_TIME = 1500;
const HIT_PADDING = 10;

let hoveredElement = null;
let dwellStart = null;
let alreadyTriggered = false;

let cursorEl = null;

// Ensure cursor exists on every page
function ensureCursor() {
    cursorEl = document.getElementById("cursor");

    if (!cursorEl) {
        cursorEl = document.createElement("div");
        cursorEl.id = "cursor";
        cursorEl.style.position = "fixed";
        cursorEl.style.width = "20px";
        cursorEl.style.height = "20px";
        cursorEl.style.borderRadius = "50%";
        cursorEl.style.background = "red";
        cursorEl.style.zIndex = "999999";
        cursorEl.style.pointerEvents = "none";
        document.body.appendChild(cursorEl);
    }
}


socket_pain.on("connect", () => {
    console.log("Gaze system connected");
});

// Cursor tracking
socket_pain.on("cursor_move", (data) => {

    ensureCursor();

    cursorEl.style.left = data.x + "px";
    cursorEl.style.top = data.y + "px";

    checkGazeTargets(data.x, data.y);
});

// Detect gaze targets
function checkGazeTargets(x, y) {

    const targets = document.querySelectorAll(".gaze-target");

    let found = false;

    targets.forEach((element) => {

        const rect = element.getBoundingClientRect();

        const inside =
            x >= rect.left - HIT_PADDING &&
            x <= rect.right + HIT_PADDING &&
            y >= rect.top - HIT_PADDING &&
            y <= rect.bottom + HIT_PADDING;

        if (inside) {
            found = true;

            // NEW target
            if (hoveredElement !== element) {
                hoveredElement = element;
                dwellStart = Date.now();
                alreadyTriggered = false;
            }

            // same target
            else {
                const elapsed = Date.now() - dwellStart;

                if (elapsed >= DWELL_TIME && !alreadyTriggered) {
                    alreadyTriggered = true;

                    triggerGazeAction(element);
                }
            }
        }
    });

    if (!found) {
        resetGazeState();
    }
}

// Action handler (GLOBAL navigation or intent)
function triggerGazeAction(element) {

    const answer = element.textContent;
    const question = document.getElementById("questionText").innerText;
    
    // CASE 2: ALS phrase selection (NEW)
    if (text) {
        socket_pain.emit("pain_gq", {
            answer: answer,
            question: question
        });

        resetGazeState();
        return;
    }
}
// Reset state
function resetGazeState() {
    hoveredElement = null;
    dwellStart = null;
    alreadyTriggered = false;
}

// Init automatically on load
window.addEventListener("DOMContentLoaded", ensureCursor);