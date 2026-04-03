from splent_framework.fixtures.fixtures import *  # noqa: F401,F403
import pytest
from splent_io.splent_feature_auth.models import User
from splent_framework.db import db


class _UserRef:
    """Lightweight reference to a user that doesn't need a SQLAlchemy session."""

    def __init__(self, id, email):
        self.id = id
        self.email = email


@pytest.fixture(scope="function")
def admin_user(test_app):
    with test_app.app_context():
        existing = User.query.filter_by(email="admin@admin.com").first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        user = User(email="admin@admin.com", active=True)
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()
        ref = _UserRef(user.id, user.email)

    yield ref

    with test_app.app_context():
        u = db.session.get(User, ref.id)
        if u:
            db.session.delete(u)
            db.session.commit()


@pytest.fixture(scope="function")
def logged_in_client(test_client, admin_user):
    test_client.post(
        "/login",
        data={"email": "admin@admin.com", "password": "admin"},
        follow_redirects=True,
    )
    return test_client
