//Dwell time configuration
const DWELL_TIME = 1500;
const HIT_PADDING = 20;

//State Initialization
let hoveredElement = null;
let dwellStart = null;
let triggered = false;

let cursorEl = null;
let isProcessingSentence = false;

//Shared socket across the website
const socket = window.socket;
let sentence_phrases = [];

//small red dot as pseudo-cursor setup
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

//Listen to socket and activate on this particular incoming request
socket.on("cursor_move", (data) => {
    ensureCursor();

    cursorEl.style.left = data.x + "px";
    cursorEl.style.top = data.y + "px";

    checkTargets(data.x, data.y);
});

//Gaze Detection for the particular tag
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

//Things to do after Gaze detection.
//2 Functionalities.
//1. If there is href -> go to the href
//2. If there is text -> send a request to the server
function triggerSelection(element) {
    const href = element.dataset.href;

    if (href) {
        window.location.href = href;
        return;
    }

    const phrase = element.textContent.trim();
    const normalized = phrase.toLowerCase();

    console.log("Selected via gaze:", phrase);

    //important, all the 
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

//Reset Gaze state.
function resetState() {
    hoveredElement = null;
    dwellStart = null;
    triggered = false;
}

//Init
window.addEventListener("DOMContentLoaded", ensureCursor);