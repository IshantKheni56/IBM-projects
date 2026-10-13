/* ═══════════════════════════════════════════════════════════════════
   NutriBot — app.js
   Client-side logic for the Nutrition Agentic AI application
   IBM Granite LLM | watsonx.ai
═══════════════════════════════════════════════════════════════════ */

"use strict";

// ── State ─────────────────────────────────────────────────────────────────────
let currentStep = 1;
let userProfile = {};
let currentPlanFile = "";
const TOTAL_STEPS = 4;

// ── Step Navigation ───────────────────────────────────────────────────────────

function showStep(step) {
  document.querySelectorAll(".form-step").forEach(s => s.classList.remove("active"));
  document.getElementById("formStep" + step).classList.add("active");
  document.querySelectorAll(".step").forEach((el, i) => {
    el.classList.remove("active", "done");
    if (i + 1 < step) el.classList.add("done");
    if (i + 1 === step) el.classList.add("active");
  });
  currentStep = step;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function nextStep(from) {
  if (!validateStep(from)) return;
  showStep(from + 1);
}

function prevStep(from) {
  showStep(from - 1);
}

// ── Validation ────────────────────────────────────────────────────────────────

function validateStep(step) {
  clearErrors();
  const errors = [];

  if (step === 1) {
    const name = val("name");
    const age = val("age");
    const city = val("city");
    const country = val("country");
    const diet = val("diet_preference");

    if (!name || name.trim().length < 2)     { errors.push("Full name is required (at least 2 characters)."); mark("name"); }
    if (!age || isNaN(age) || +age < 5 || +age > 120) { errors.push("Age must be between 5 and 120."); mark("age"); }
    if (!city || city.trim().length < 2)     { errors.push("City is required."); mark("city"); }
    if (!country || country.trim().length < 2){ errors.push("Country is required."); mark("country"); }
    if (!diet)                               { errors.push("Please select a diet preference."); mark("diet_preference"); }
  }

  if (step === 3) {
    const goals = getCheckedValues(".goal-check");
    const custom = val("goals_custom");
    if (goals.length === 0 && !custom.trim()) {
      errors.push("Please select at least one health goal.");
    }
  }

  if (errors.length > 0) {
    showErrors(errors, "formStep" + step);
    return false;
  }
  return true;
}

function val(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : "";
}

function mark(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("error");
}

function clearErrors() {
  document.querySelectorAll(".error-list").forEach(e => e.remove());
  document.querySelectorAll(".error").forEach(e => e.classList.remove("error"));
}

function showErrors(errors, stepId) {
  const container = document.getElementById(stepId);
  const div = document.createElement("div");
  div.className = "error-list";
  div.innerHTML = `<p>Please fix the following:</p><ul>${errors.map(e => `<li>${e}</li>`).join("")}</ul>`;
  container.querySelector(".step-header").insertAdjacentElement("afterend", div);
}

// ── Medical Conditions Helper ─────────────────────────────────────────────────

function toggleNone(checkbox) {
  const others = document.querySelectorAll(".med-check");
  if (checkbox.checked) {
    others.forEach(cb => { cb.checked = false; });
  }
}

function getCheckedValues(selector) {
  return Array.from(document.querySelectorAll(selector))
    .filter(cb => cb.checked)
    .map(cb => cb.value);
}

function getMedicalHistory() {
  const noneChecked = document.getElementById("med_none").checked;
  if (noneChecked) return "None";
  const selected = getCheckedValues(".med-check");
  const other = val("medical_history_other");
  const all = [...selected, ...(other ? [other] : [])];
  return all.length > 0 ? all.join(", ") : "None";
}

// ── Generate Plan ─────────────────────────────────────────────────────────────

async function generatePlan() {
  if (!validateStep(3)) return;

  const goals = getCheckedValues(".goal-check");
  const goalsCustom = val("goals_custom");
  const allGoals = [...goals, ...(goalsCustom ? [goalsCustom] : [])].join(", ") || "General Wellness";

  userProfile = {
    name:             val("name"),
    age:              val("age"),
    gender:           val("gender") || "Not specified",
    city:             val("city"),
    country:          val("country"),
    diet_preference:  val("diet_preference"),
    medical_history:  getMedicalHistory(),
    allergies:        val("allergies") || "None",
    weight:           val("weight") || "",
    height:           val("height") || "",
    activity_level:   val("activity_level"),
    goals:            allGoals
  };

  showLoading(true);
  animateLoadingSteps();

  try {
    const resp = await fetch("/api/generate-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userProfile)
    });
    const data = await resp.json();
    showLoading(false);

    if (!data.success) {
      showStep(1);
      showErrors(data.errors || ["An error occurred. Please try again."], "formStep1");
      return;
    }

    displayPlan(data);
    showStep(4);

  } catch (err) {
    showLoading(false);
    alert("Network error: " + err.message + "\nPlease ensure the server is running.");
  }
}

function displayPlan(data) {
  // Heading
  document.getElementById("planHeading").textContent =
    `${data.user_name}'s Personalised Nutrition Plan`;
  document.getElementById("planSubtitle").textContent =
    `Generated on ${data.timestamp} · IBM Granite LLM · watsonx.ai`;

  // Warnings
  const wb = document.getElementById("warningsBox");
  if (data.warnings && data.warnings.length > 0) {
    wb.innerHTML = "⚠️ <strong>Important Notice:</strong><br>" +
      data.warnings.map(w => `<p style="margin-top:6px">${w}</p>`).join("");
    wb.style.display = "block";
  } else {
    wb.style.display = "none";
  }

  // Render markdown plan
  const planDiv = document.getElementById("planOutput");
  if (typeof marked !== "undefined") {
    marked.setOptions({ breaks: true, gfm: true });
    planDiv.innerHTML = marked.parse(data.plan || "");
  } else {
    planDiv.innerHTML = "<pre>" + (data.plan || "") + "</pre>";
  }

  currentPlanFile = data.plan_file || "";

  // Add welcome chat message
  appendChatMessage("bot",
    `Hi **${data.user_name}**! 👋 Your personalised nutrition plan is ready. Feel free to ask me any questions about your plan or nutrition in general — I'm here to help!`
  );
}

// ── Download Plan ─────────────────────────────────────────────────────────────

function downloadPlan() {
  if (!currentPlanFile) {
    alert("No plan file found. Please generate a plan first.");
    return;
  }
  window.location.href = "/api/download-plan/" + encodeURIComponent(currentPlanFile);
}

// ── Reset Form ────────────────────────────────────────────────────────────────

function resetForm() {
  if (!confirm("Start over? This will clear your current plan.")) return;
  document.querySelector("form") && document.querySelector("form").reset();
  // Reset individual fields
  ["name","age","city","country","allergies","weight","height",
   "goals_custom","medical_history_other"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
  document.querySelectorAll("input[type=checkbox]").forEach(cb => cb.checked = false);
  document.getElementById("gender").value = "";
  document.getElementById("diet_preference").value = "";
  document.getElementById("activity_level").value = "Moderate";

  // Reset chat
  const cw = document.getElementById("chatWindow");
  cw.innerHTML = `
    <div class="chat-message bot-message">
      <div class="chat-avatar">🤖</div>
      <div class="chat-bubble">Hi! I'm NutriBot. You can ask me any nutrition-related questions — about your plan, healthy eating, recipes, or general wellness. How can I help you today?</div>
    </div>`;

  userProfile = {};
  currentPlanFile = "";
  showStep(1);
}

// ── Q&A Agent ─────────────────────────────────────────────────────────────────

async function sendQuery() {
  const input = document.getElementById("userQuestion");
  const question = input.value.trim();
  if (!question) return;

  input.value = "";
  appendChatMessage("user", question);

  // Typing indicator
  const typingId = "typing-" + Date.now();
  const cw = document.getElementById("chatWindow");
  cw.insertAdjacentHTML("beforeend", `
    <div class="chat-message bot-message typing-indicator" id="${typingId}">
      <div class="chat-avatar">🤖</div>
      <div class="chat-bubble">NutriBot is thinking…</div>
    </div>`);
  cw.scrollTop = cw.scrollHeight;

  try {
    const resp = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, context: userProfile })
    });
    const data = await resp.json();
    document.getElementById(typingId)?.remove();

    if (data.success) {
      appendChatMessage("bot", data.answer);
    } else {
      appendChatMessage("bot", "⚠️ " + (data.answer || "I'm unable to answer that right now. Please try again."));
    }
  } catch (err) {
    document.getElementById(typingId)?.remove();
    appendChatMessage("bot", "❌ Connection error. Please check that the server is running.");
  }
}

function askQuick(question) {
  document.getElementById("userQuestion").value = question;
  sendQuery();
}

function appendChatMessage(role, text) {
  const cw = document.getElementById("chatWindow");
  const isBot = role === "bot";
  const html = `
    <div class="chat-message ${isBot ? "bot-message" : "user-message"}">
      <div class="chat-avatar">${isBot ? "🤖" : "👤"}</div>
      <div class="chat-bubble">${isBot
        ? (typeof marked !== "undefined" ? marked.parse(text) : text)
        : escapeHtml(text)
      }</div>
    </div>`;
  cw.insertAdjacentHTML("beforeend", html);
  cw.scrollTop = cw.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Loading ───────────────────────────────────────────────────────────────────

function showLoading(show) {
  document.getElementById("loadingOverlay").style.display = show ? "flex" : "none";
}

function animateLoadingSteps() {
  const steps = ["ls1", "ls2", "ls3", "ls4"];
  let i = 0;
  const interval = setInterval(() => {
    if (i > 0) {
      const prev = document.getElementById(steps[i - 1]);
      if (prev) { prev.classList.remove("active"); prev.classList.add("done"); }
    }
    if (i < steps.length) {
      const curr = document.getElementById(steps[i]);
      if (curr) curr.classList.add("active");
      i++;
    } else {
      clearInterval(interval);
    }
  }, 900);
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  showStep(1);
  // Allow Enter on text fields in step 1/2 to move forward
  document.querySelectorAll("input[type=text], input[type=number]").forEach(input => {
    input.addEventListener("keypress", e => {
      if (e.key === "Enter" && currentStep < 3) nextStep(currentStep);
    });
  });
});
