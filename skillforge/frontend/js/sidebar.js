// ---------- Sidebar (rendered on every page) ----------
const NAV_ITEMS = [
  { href: "index.html", label: "About", key: "about" },
  { href: "skills.html", label: "Skills", key: "skills" },
  { href: "expenses.html", label: "Expenses", key: "expenses" },
  { href: "analysis.html", label: "Gap Analysis", key: "analysis" },
  { href: "plan.html", label: "Weekly Plan", key: "plan" },
];

function renderSidebar(activeKey) {
  const links = NAV_ITEMS.map(
    (item) => `
    <a class="nav-link ${item.key === activeKey ? "active" : ""}" href="${item.href}">
      <span class="dot"></span>${item.label}
    </a>`,
  ).join("");

  return `
    <aside class="sidebar">
      <div class="brand">Skill<span>Forge</span></div>
      ${links}
      <div class="sidebar-footer">
        AI Career + Finance Co-Pilot<br/>for Engineering Students
      </div>
    </aside>
  `;
}

document.addEventListener("DOMContentLoaded", () => {
  const mount = document.getElementById("sidebar-mount");
  if (mount) mount.outerHTML = renderSidebar(mount.dataset.active);
});
