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
});
