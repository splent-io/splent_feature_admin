"""
Functional tests for admin routes.

Tests use Flask's test client to exercise full HTTP
request/response cycles (GET, POST, redirects, rendered HTML).
"""


def test_dashboard_requires_login(test_client):
    response = test_client.get("/admin", follow_redirects=False)
    assert response.status_code in (302, 401)


def test_dashboard_accessible_when_logged_in(logged_in_client):
    response = logged_in_client.get("/admin")
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data


def test_model_list_requires_login(test_client):
    response = test_client.get("/admin/User", follow_redirects=False)
    assert response.status_code in (302, 401)


def test_model_list_accessible_when_logged_in(logged_in_client):
    response = logged_in_client.get("/admin/User")
    assert response.status_code == 200
    assert b"User" in response.data


def test_unknown_model_redirects_to_dashboard(logged_in_client):
    response = logged_in_client.get("/admin/NonExistentModel", follow_redirects=True)
    assert b"not found" in response.data


def test_create_form_renders(logged_in_client):
    response = logged_in_client.get("/admin/User/create")
    assert response.status_code == 200
    assert b"Create" in response.data


def test_delete_nonexistent_record_redirects(logged_in_client):
    response = logged_in_client.get("/admin/User/99999/delete", follow_redirects=True)
    assert b"not found" in response.data
