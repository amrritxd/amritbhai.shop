// Amritt Edition - notification service worker (site root par /sw.js ke naam se rakhein)
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));

// Notification par tap -> test page khule (ya pehle se khula ho to uspar aaye)
self.addEventListener("notificationclick", e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || "/test.html";
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
    for (const c of list) { if ("focus" in c) return c.focus(); }
    return self.clients.openWindow(url);
  }));
});

// Future ke liye: server se push aaye (FCM / Web Push) to bhi notification dikhe
self.addEventListener("push", e => {
  let d = {}; try { d = e.data ? e.data.json() : {}; } catch (_) {}
  e.waitUntil(self.registration.showNotification(d.title || "Amritt Edition", {
    body: d.body || "", icon: "/apple-touch-icon.png", badge: "/favicon.ico", data: { url: d.url || "/test.html" }
  }));
});
