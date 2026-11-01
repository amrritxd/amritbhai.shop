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

// Server se push (FCM / Web Push) aaye to notification dikhaye
self.addEventListener("push", e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (_) { try { d = { body: e.data.text() }; } catch (__) {} }
  // FCM Console: { notification: { title, body }, data: {...} }  |  data-only: { title, body, url }
  const n = d.notification || {};
  const x = d.data || {};
  const title = n.title || x.title || d.title || "Amritt Edition";
  const body = n.body || x.body || d.body || "";
  const url = x.url || d.url || (d.fcmOptions && d.fcmOptions.link) || (n.click_action) || "/test.html";
  e.waitUntil(self.registration.showNotification(title, {
    body, icon: "/apple-touch-icon.png", badge: "/favicon.ico", data: { url }
  }));
});
