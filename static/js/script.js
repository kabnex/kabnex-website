// =========================================================
// KABNEX — shared front-end behaviour
// =========================================================

document.addEventListener("DOMContentLoaded", () => {
  initNavToggle();
  initScrollReveal();
  initTerminalTyping();
  initContactForm();
});

/* ---------- Mobile nav toggle ---------- */
function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (!toggle || !links) return;

  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  links.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      links.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

/* ---------- Scroll reveal ---------- */
function initScrollReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;

  if (!("IntersectionObserver" in window)) {
    items.forEach((el) => el.classList.add("in"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  items.forEach((el) => observer.observe(el));
}

/* ---------- Terminal typing effect (home hero) ---------- */
function initTerminalTyping() {
  const el = document.querySelector("[data-terminal-type]");
  if (!el) return;

  const lines = JSON.parse(el.getAttribute("data-terminal-type"));
  const speed = 26; // ms per character
  const linePause = 380; // ms pause after a line completes

  el.innerHTML = "";
  let lineIndex = 0;

  const cursor = document.createElement("span");
  cursor.className = "cursor";

  function typeLine() {
    if (lineIndex >= lines.length) {
      el.appendChild(cursor);
      return;
    }
    const { text, className } = lines[lineIndex];
    const lineEl = document.createElement("div");
    const span = document.createElement("span");
    span.className = className || "out";
    lineEl.appendChild(span);
    el.appendChild(lineEl);

    let charIndex = 0;
    (function typeChar() {
      if (charIndex < text.length) {
        span.textContent += text.charAt(charIndex);
        charIndex += 1;
        setTimeout(typeChar, speed);
      } else {
        lineIndex += 1;
        setTimeout(typeLine, linePause);
      }
    })();
  }

  typeLine();
}

/* ---------- Contact form ---------- */
function initContactForm() {
  const form = document.getElementById("contact-form");
  if (!form) return;

  const note = document.getElementById("form-note");
  const submitBtn = form.querySelector("button[type='submit']");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    note.textContent = "";
    note.className = "form-note";

    const payload = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      service: form.service.value,
      message: form.message.value.trim(),
    };

    if (!payload.name || !payload.email || !payload.message) {
      note.textContent = "$ error: please fill in your name, email, and message.";
      note.classList.add("error");
      return;
    }

    submitBtn.disabled = true;
    const originalLabel = submitBtn.textContent;
    submitBtn.textContent = "sending...";

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (response.ok && data.status === "ok") {
        note.textContent = "$ message sent \u2713 we'll reply within 1-2 business days.";
        note.classList.add("success");
        form.reset();
      } else {
        note.textContent = "$ error: " + (data.message || "something went wrong. please try again.");
        note.classList.add("error");
      }
    } catch (err) {
      note.textContent = "$ error: could not reach the server. please try again shortly.";
      note.classList.add("error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalLabel;
    }
  });
}
