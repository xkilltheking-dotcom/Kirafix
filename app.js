const routes = {
  home: "index.html",
  profile: "profile.html",
  settings: "settings.html"
};

async function loadPage(page) {
  try {
    const res = await fetch(routes[page]);
    const html = await res.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    const newContent = doc.body.innerHTML;

    document.getElementById("app").innerHTML = newContent;

    // تشغيل السكربتات اللي جوه الصفحة
    doc.querySelectorAll("script").forEach(oldScript => {
      const newScript = document.createElement("script");

      if (oldScript.src) {
        newScript.src = oldScript.src;
      } else {
        newScript.textContent = oldScript.textContent;
      }

      document.body.appendChild(newScript);
    });

  } catch (e) {
    console.error("Page load error:", e);
  }
}

// Navigation
document.addEventListener("click", (e) => {
  if (e.target.matches("[data-link]")) {
    e.preventDefault();
    const page = e.target.getAttribute("data-link");
    history.pushState({}, "", page);
    loadPage(page);
  }
});

// back/forward
window.onpopstate = () => {
  const page = location.pathname.replace("/", "") || "home";
  loadPage(page);
};

// أول تحميل
window.onload = () => {
  const page = location.pathname.replace("/", "") || "home";
  loadPage(page);
};
