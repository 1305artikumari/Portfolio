document.addEventListener("DOMContentLoaded", () => {
  // Mobile Menu Toggle
  const menuBtn = document.getElementById("menu-btn");
  const navLinks = document.getElementById("nav-links");

  menuBtn?.addEventListener("click", () => {
    navLinks?.classList.toggle("open");
  });

  // Smooth scroll for internal anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href").slice(1);
      if (!targetId) return;
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
        navLinks?.classList.remove("open");
        try {
          history.pushState(null, null, "#" + targetId);
        } catch (_) {}
      }
    });
  });

  // Number Counter Animation
  function animateCount(node) {
    if (node.dataset.done) return;
    node.dataset.done = "1";
    const end = Number(node.dataset.count);
    const decimals = Number(node.dataset.decimals || 0);
    const suffix = node.dataset.suffix || "";
    const start = performance.now();
    const duration = 1100;

    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      node.textContent = `${(end * eased).toFixed(decimals)}${suffix}`;
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // Animate stat counters immediately if visible
  document.querySelectorAll("[data-count]").forEach((el) => {
    animateCount(el);
  });

  // Intersection Observer for scroll animations
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("in");
        const counter = entry.target.querySelector("[data-count]");
        if (counter) animateCount(counter);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.01, rootMargin: "100px 0px 100px 0px" }
  );

  const targets = document.querySelectorAll(
    ".section, .project, .work-card, .edu-card, .goals li, .skill, .stat-card"
  );
  targets.forEach((el) => {
    el.classList.add("in"); // Ensure visible right away
    observer.observe(el);
  });

  // Contact Form AJAX Handler (Works inside iframes & on all web browsers)
  const contactForm = document.getElementById("contact-form");
  const contactSubmit = document.getElementById("contact-submit");
  const contactStatus = document.getElementById("contact-status");

  if (contactForm) {
    contactForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const name = document.getElementById("contact-name")?.value.trim() || "";
      const email = document.getElementById("contact-email")?.value.trim() || "";
      const subject = document.getElementById("contact-subject")?.value.trim() || "Portfolio Inquiry";
      const message = document.getElementById("contact-message")?.value.trim() || "";

      if (!name || !email || !message) {
        if (contactStatus) {
          contactStatus.style.display = "block";
          contactStatus.innerHTML = '<p style="color:#ff7a90; margin-top:8px;">Please fill in all required fields.</p>';
        }
        return;
      }

      if (contactSubmit) {
        contactSubmit.disabled = true;
        contactSubmit.textContent = "Sending message...";
      }

      try {
        const response = await fetch("https://formsubmit.co/ajax/artikumari09011999@gmail.com", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
          },
          body: JSON.stringify({
            name: name,
            email: email,
            _subject: `Portfolio Message: ${subject} from ${name}`,
            message: message,
          }),
        });

        const result = await response.json();

        if (response.ok || result.success === "true" || result.success === true) {
          contactForm.innerHTML = `
            <div style="background: rgba(62, 224, 178, 0.12); border: 1px solid rgba(62, 224, 178, 0.4); border-radius: 14px; padding: 24px; text-align: center; margin-top: 10px;">
              <h3 style="color: #3ee0b2; margin: 0 0 8px;">✅ Message Sent Successfully!</h3>
              <p style="color: #cbd5e1; margin: 0; line-height: 1.6;">
                Thank you, <b>${name}</b>! Your message has been delivered directly to <b>artikumari09011999@gmail.com</b>. I will reply soon.
              </p>
            </div>
          `;
        } else {
          throw new Error("Submission failed");
        }
      } catch (err) {
        // Graceful fallback to mailto link
        const mailtoUrl = `mailto:artikumari09011999@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`)}`;
        window.open(mailtoUrl, "_blank");

        if (contactStatus) {
          contactStatus.style.display = "block";
          contactStatus.innerHTML = `
            <div style="background: rgba(232, 192, 122, 0.15); border: 1px solid rgba(232, 192, 122, 0.4); border-radius: 12px; padding: 14px; margin-top: 12px;">
              <p style="color:#e8c07a; margin:0; font-size:0.9rem;">
                Email app opened! You can also email directly to <a href="mailto:artikumari09011999@gmail.com" style="color:#3ee0b2; text-decoration:underline;">artikumari09011999@gmail.com</a>.
              </p>
            </div>
          `;
        }
        if (contactSubmit) {
          contactSubmit.disabled = false;
          contactSubmit.textContent = "Send message";
        }
      }
    });
  }
});
