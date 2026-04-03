from splent_framework.hooks.template_hooks import register_template_hook
from flask import request, url_for


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


register_template_hook("layout.authenticated_sidebar", admin_sidebar_link)
