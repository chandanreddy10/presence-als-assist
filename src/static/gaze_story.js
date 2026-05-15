// socket_story connection (shared across all pages)
const socket_story = window.socket;

const DWELL_TIME = 3000;
const HIT_PADDING = 10;

let hoveredElement = null;
let dwellStart = null;
let alreadyTriggered = false;
let InProgress = false;
let lastSentText = null;
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

// Socket connected
socket_story.on("connect", () => {
    console.log("Gaze system connected");
});

socket_story.on("story_ack", () => {
    console.log("✅ Server acknowledged, unlocking");
    InProgress = false;
});

// Cursor tracking
socket_story.on("cursor_move", (data) => {

    ensureCursor();

    cursorEl.style.left = data.x + "px";
    cursorEl.style.top = data.y + "px";

    checkGazeTargets(data.x, data.y);
});

// Detect gaze targets
function checkGazeTargets(x, y) {

    if (InProgress) return;

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

            // SAME target
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

// Action handler
function triggerGazeAction(element) {

    if (InProgress) return;

    const href = element.dataset.href;
    const text = element.textContent?.trim();

    if (text && text === lastSentText) {
        console.log("Duplicate ignored:", text);
        return;
    }

    console.log("Triggered:", href || text);

    // CASE 1: navigation
    if (href) {
        InProgress = true;
        window.location.href = href;
        return;
    }

    // CASE 2: ALS phrase selection
    if (text) {
        InProgress = true;

        lastSentText = text;

        socket_story.emit("story_text", {
            text: text
        });

        resetGazeState();
    }
}

// Update options from server
socket_story.on("update_options", (data) => {
    console.log("received update_options:", data);
    const options = data.options || [];

    if (options.length < 3) {
        console.warn("Not enough options:", options);
        return;
    }

    document.getElementById("option-1").textContent = options[0];
    document.getElementById("option-2").textContent = options[1];
    document.getElementById("option-3").textContent = options[2];
});

// Reset state
function resetGazeState() {
    hoveredElement = null;
    dwellStart = null;
    alreadyTriggered = false;
}

// Init automatically on load
window.addEventListener("DOMContentLoaded", ensureCursor);