from splent_framework.hooks.template_hooks import register_template_hook
from flask import request, url_for
from flask_login import current_user
from markupsafe import escape


def admin_sidebar_link():
    active = (
        "active" if request.endpoint and request.endpoint.startswith("admin.") else ""
    )
    return (
        f'<li class="sidebar-item {active}">'
        f'<a class="sidebar-link" href="{url_for("admin.dashboard")}">'
        '<i class="align-middle" data-feather="settings"></i> '
        '<span class="align-middle">Admin</span>'
        "</a>"
        "</li>"
    )


# WordPress-style fixed top bar. CSS is inlined so it works on any public page
# (no feather icons there). The body offset only applies when the bar renders.
_ADMIN_BAR_CSS = (
    "<style>"
    "#sp-adminbar{position:fixed;top:0;left:0;right:0;height:32px;background:#1d2327;"
    "color:#f0f0f1;display:flex;align-items:center;padding:0 6px;z-index:99999;"
    "font:13px/32px -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
    "box-shadow:0 1px 3px rgba(0,0,0,.25)}"
    "#sp-adminbar a{color:#f0f0f1;text-decoration:none;padding:0 10px;height:32px;"
    "display:inline-flex;align-items:center}"
    "#sp-adminbar a:hover{color:#72aee6;background:#2c3338}"
    "#sp-adminbar .sp-adminbar__brand{font-weight:600}"
    "#sp-adminbar .sp-adminbar__spacer{flex:1}"
    "#sp-adminbar .sp-adminbar__me{opacity:.7;padding:0 10px}"
    "body.cms-public{padding-top:32px}"
    "</style>"
)


def admin_bar():
    """Top admin bar shown only to authenticated users (WordPress style).

    Rendered into the public shell through the ``layout.body_start`` hook, so it
    appears on every public page with quick access to the dashboard and logout.
    """
    if not (current_user and getattr(current_user, "is_authenticated", False)):
        return ""
    email = escape(getattr(current_user, "email", None) or "Account")
    return (
        _ADMIN_BAR_CSS + '<div id="sp-adminbar">'
        f'<a class="sp-adminbar__brand" href="{url_for("admin.dashboard")}">&#9881; Dashboard</a>'
        '<a href="/">View site</a>'
        '<span class="sp-adminbar__spacer"></span>'
        f'<span class="sp-adminbar__me">{email}</span>'
        f'<a href="{url_for("auth.logout")}">Log out</a>'
        "</div>"
    )


register_template_hook("layout.authenticated_sidebar", admin_sidebar_link)
register_template_hook("layout.body_start", admin_bar)
