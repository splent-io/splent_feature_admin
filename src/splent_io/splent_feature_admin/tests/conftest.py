from splent_framework.fixtures.fixtures import *  # noqa: F401,F403
import pytest
from splent_io.splent_feature_auth.models import User
from splent_framework.db import db


@pytest.fixture(scope="function")
def admin_user(test_app):
    with test_app.app_context():
        user = User(email="admin@admin.com", active=True)
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()
        db.session.expunge(user)
        return user


@pytest.fixture(scope="function")
def logged_in_client(test_client, admin_user):
    test_client.post(
        "/login",
        data={"email": "admin@admin.com", "password": "admin"},
        follow_redirects=True,
    )
    return test_client
