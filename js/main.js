document.getElementById("menu-btn")?.addEventListener("click", () => {
  document.getElementById("nav-links")?.classList.toggle("open");
});

document.getElementById("nav-links")?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    document.getElementById("nav-links")?.classList.remove("open");
  });
});

function animateCount(node) {
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

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("in");
      if (entry.target.classList.contains("stat-card")) {
        const value = entry.target.querySelector("[data-count]");
        if (value && !value.dataset.done) {
          value.dataset.done = "1";
          animateCount(value);
        }
      }
      observer.unobserve(entry.target);
    });
  },
  { threshold: 0.15 }
);

document
  .querySelectorAll(".section, .project, .work-card, .edu-card, .goals li, .skill, .stat-card")
  .forEach((el) => observer.observe(el));
