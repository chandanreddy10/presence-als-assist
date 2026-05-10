// ================================
// CONFIG
// ================================
const DWELL_TIME = 1500;
const HIT_PADDING = 20;

// ================================
// STATE
// ================================
let hoveredElement = null;
let dwellStart = null;
let triggered = false;

let cursorEl = null;
let isProcessingSentence = false;
// ================================
// SOCKET (GLOBAL SHARED)
// ================================
const socket = window.socket;
let sentence_phrases = [];
// ================================
// CURSOR SETUP
// ================================
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

// ================================
// SOCKET LISTEN (GAZE STREAM)
// ================================
socket.on("cursor_move", (data) => {
    ensureCursor();

    cursorEl.style.left = data.x + "px";
    cursorEl.style.top = data.y + "px";

    checkTargets(data.x, data.y);
});

// ================================
// GAZE DETECTION
// ================================
function checkTargets(x, y) {
    const targets = document.querySelectorAll(".gaze-target");

    let found = false;

    targets.forEach((el) => {
        const rect = el.getBoundingClientRect();

        const inside =
            x >= rect.left - HIT_PADDING &&
            x <= rect.right + HIT_PADDING &&
            y >= rect.top - HIT_PADDING &&
            y <= rect.bottom + HIT_PADDING;

        if (inside) {
            found = true;

            if (hoveredElement !== el) {
                hoveredElement = el;
                dwellStart = Date.now();
                triggered = false;
            } else {
                const elapsed = Date.now() - dwellStart;

                if (elapsed >= DWELL_TIME && !triggered) {
                    triggered = true;
                    triggerSelection(el);
                }
            }
        }
    });

    if (!found) resetState();
}

// ================================ 
// TRIGGER SELECTION (IMPORTANT CHANGE)
// ================================
// function triggerSelection(element) {
//     const phrase = element.textContent.trim();
//     const normalized = phrase.toLowerCase();

//     console.log("Selected via gaze:", phrase);

//     // ONLY when the word is exactly "end"
//     if (normalized === "end") {

//         console.log("Final sentence:", sentence_phrases);

//         socket.emit("sentence", {
//             sentence: sentence_phrases
//         });

//         // reset after sending
//         sentence_phrases = [];
//         baseDisabled = false;

//         resetState();
//         return;
//     }

//     // normal phrase flow
//     const exists = sentence_phrases.some(
//         p => p.toLowerCase() === normalized
//     );

//     if (!exists) {
//         sentence_phrases.push(phrase);

//         socket.emit("phrase_selected", {
//             sentence: sentence_phrases
//         });
//     } else {
//         console.log("Already selected:", phrase);
//     }

//     baseDisabled = true;
//     resetState();
// }
function triggerSelection(element) {
    const phrase = element.textContent.trim();
    const normalized = phrase.toLowerCase();

    console.log("Selected via gaze:", phrase);

    // 🔴 BLOCK ALL INPUT WHILE PROCESSING
    if (isProcessingSentence) {
        console.log("Waiting for previous sentence to finish...");
        return;
    }

    // ONLY when word is "end"
    if (normalized === "end") {

        // isProcessingSentence = true; // 

        console.log("Final sentence:", sentence_phrases);

        socket.emit("sentence", {
            sentence: sentence_phrases
        });
        sentence_phrases = [];

        resetState();
        return;
    }

    // 🟢 normal phrase selection
    const exists = sentence_phrases.some(
        p => p.toLowerCase() === normalized
    );

    if (!exists) {
        sentence_phrases.push(phrase);

        socket.emit("phrase_selected", {
            phrase: phrase,
            sentence: sentence_phrases
        });
    }

    baseDisabled = true;
    resetState();
}
// ================================
// RESET
// ================================
function resetState() {
    hoveredElement = null;
    dwellStart = null;
    triggered = false;
}

// ================================
// INIT
// ================================
window.addEventListener("DOMContentLoaded", ensureCursor);