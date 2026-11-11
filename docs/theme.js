(function () {
  const key = "agent-lib-theme";
  const saved = localStorage.getItem(key);
  const preferDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (preferDark ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", theme);
  window.toggleTheme = function () {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(key, next);
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = next === "dark" ? "浅色" : "深色";
  };
  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "浅色" : "深色";
  });
})();
