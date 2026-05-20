"""Inject PWA manifest, meta tags, and service-worker registration into the
parent (top-level) document. Needed because Streamlit content runs inside an
iframe, and a PWA manifest must live on the top-level page for browsers to
recognize the app as installable."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


_INJECTION_HTML = """
<script>
(function () {
  try {
    const top = window.parent && window.parent.document ? window.parent.document : document;
    if (top.querySelector('link[data-pwa="diamond-qc"]')) return;  // already injected

    function add(tag, attrs) {
      const el = top.createElement(tag);
      Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
      top.head.appendChild(el);
      return el;
    }

    add("link", {
      rel: "manifest",
      href: "/app/static/manifest.json",
      "data-pwa": "diamond-qc",
    });
    add("meta",  { name: "theme-color",                  content: "#0F1116" });
    add("meta",  { name: "mobile-web-app-capable",       content: "yes" });
    add("meta",  { name: "apple-mobile-web-app-capable", content: "yes" });
    add("meta",  { name: "apple-mobile-web-app-title",   content: "Diamond QC" });
    add("meta",  { name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" });
    add("link",  { rel: "apple-touch-icon", href: "/app/static/icon-192.png" });
    add("link",  { rel: "icon", type: "image/png", sizes: "64x64", href: "/app/static/favicon.png" });

    // NOTE: No service worker. Streamlit only serves static files under
    // /app/static/, and a SW registered from there cannot legally take scope
    // '/' without a Service-Worker-Allowed response header (which Streamlit
    // doesn't expose). Modern Chrome (2021+) makes the app installable from
    // the manifest alone, so we skip SW registration.
  } catch (e) {
    console.warn("[PWA] injection error:", e);
  }
})();
</script>
"""


def inject_pwa() -> None:
    """Call once early in app.py (after st.set_page_config)."""
    if st.session_state.get("_pwa_injected"):
        return
    components.html(_INJECTION_HTML, height=0)
    st.session_state["_pwa_injected"] = True
