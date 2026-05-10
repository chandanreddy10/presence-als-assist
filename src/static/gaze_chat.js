const socket_chat = window.socket;

// ================================
// STATE
// ================================
let sentence = [];
let dynamicPhrases = [];
let baseDisabled = false;

// ================================
// BASE PHRASES
// ================================
const basePhrases = [
  { id: "feel", text: "I feel", type: "emotion", x: "35%", y: "5%" },
  { id: "need", text: "Need", type: "need", x: "5%", y: "25%" },
  { id: "help", text: "Help", type: "urgent", x: "80%", y: "10%" },
  { id: "water", text: "Water", type: "need", x: "25%", y: "65%" },
  { id: "hungry", text: "Hungry", type: "need", x: "70%", y: "40%" },
  { id: "thank", text: "Thank you", type: "social", x: "75%", y: "75%" }
];

// ================================
// FIXED POSITIONS
// ================================
const layoutPositions = [
  { x: "10%", y: "20%" },
  { x: "30%", y: "20%" },
  { x: "50%", y: "20%" },
  { x: "70%", y: "20%" },
  { x: "10%", y: "50%" },
  { x: "30%", y: "50%" },
  { x: "50%", y: "50%" },
  { x: "70%", y: "50%" }
];

// ================================
// STYLE SYSTEM
// ================================
function getStyle(type) {
  switch (type) {
    case "need":
      return "bg-gradient-to-br from-sky-200/70 to-cyan-100/40 text-slate-900";
    case "urgent":
      return "bg-gradient-to-br from-red-200/70 to-rose-100/40 text-red-900";
    case "emotion":
      return "bg-gradient-to-br from-purple-200/70 to-indigo-100/40 text-indigo-900";
    case "social":
      return "bg-gradient-to-br from-emerald-200/70 to-green-100/40 text-green-900";
    case "selected":
      return "bg-gradient-to-br from-yellow-200/80 to-amber-100/50 text-black";
    default:
      return "bg-white/60 text-slate-800";
  }
}

// ================================
// PHRASE COMBINATION LOGIC
// ================================
function allPhrases() {

  const selected = sentence.map((text, i) => {
    const pos = layoutPositions[i % layoutPositions.length];
    return {
      text,
      type: "selected",
      x: pos.x,
      y: pos.y
    };
  });

  // 🚨 BASE ONLY EXISTS BEFORE FIRST SELECTION
  if (!baseDisabled) {
    return [...basePhrases, ...selected, ...dynamicPhrases];
  }
  console.log([...selected, ...dynamicPhrases]);

  return [...selected, ...dynamicPhrases];
}

// ================================
// RENDER
// ================================
function render() {
  const container = document.getElementById("phrase-container");
  if (!container) return;

  container.innerHTML = "";

  allPhrases().forEach((p) => {
    const btn = document.createElement("button");

    btn.className = `
      gaze-target
      px-10 py-10
      min-w-[260px] min-h-[160px]
      rounded-2xl
      backdrop-blur-xl
      border border-white/40
      shadow-[0_20px_60px_rgba(0,0,0,0.08)]
      flex items-center justify-center
      transition-all duration-300
      hover:scale-105 hover:shadow-[0_30px_80px_rgba(0,0,0,0.15)]
      select-none
    `;

    btn.className += " " + getStyle(p.type);

    btn.innerHTML = `
      <span class="text-5xl font-bold text-center">
        ${p.text}
      </span>
    `;

    btn.onclick = () => selectPhrase(p.text);

    container.appendChild(btn);
  });
}

//sentence render
function render_sentence() {
  const container = document.getElementById("sentence-bar");
  if (!container) return;

  container.innerHTML = "";

  sentence_phrases.forEach((p) => {
    const btn = document.createElement("button");

    btn.className = `
      px-10 py-10
      min-w-[260px] min-h-[160px]
      rounded-2xl
      backdrop-blur-xl
      border border-white/40
      shadow-[0_20px_60px_rgba(0,0,0,0.08)]
      flex items-center justify-center
      transition-all duration-300
      hover:scale-105 hover:shadow-[0_30px_80px_rgba(0,0,0,0.15)]
      select-none
      ${getStyle("social")}
    `;

    btn.innerHTML = `
      <span class="text-5xl font-bold text-center">
        ${p}
      </span>
    `;

    container.appendChild(btn);
  });
}
// ================================
// SELECTION LOGIC
// ================================
// function selectPhrase(text) {
//   sentence.push(text);

//   // 🚨 FIRST SELECTION DISABLES BASE PHRASES
//   baseDisabled = true;

//   socket_chat.emit("phrase_selected", {
//     phrase: text,
//     sentence: sentence
//   });

//   render();
// }

// ================================
// SERVER UPDATES (FULL REPLACE)
// ================================
socket_chat.on("new_phrases", (data) => {
//   console.log(data);
  const incoming = data.phrases.text;
//   console.log(incoming);
  dynamicPhrases = incoming.map((p, index) => {
    const pos = layoutPositions[index % layoutPositions.length];

    return {
      text: p,
      type: p.type,
      x: pos.x,
      y: pos.y
    };
  });

  render();
  console.log(sentence_phrases);
  render_sentence();
});

// ================================
// RESET
// ================================
socket_chat.on("reset_sentence", () => {
  sentence = [];
  baseDisabled = false; // 🔄 restore base screen
  render();
});

// ================================
// INIT
// ================================
window.addEventListener("DOMContentLoaded", render);