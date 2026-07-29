"""
Integration tests for the generic CRUD's protected-column deny list.

The auto-CRUD reaches every model in the product, so it must not be the
back door to the columns that decide who may read what: a role write would
be privilege escalation, and rewriting a media item's owner or filename
would re-point a restricted file at a permissive resolver while keeping the
unreleased bytes.
"""

import pytest

from splent_io.splent_feature_admin.services import AdminService
from splent_io.splent_feature_auth.models import User
from splent_framework.db import db


def test_role_is_not_editable(test_app):
    with test_app.app_context():
        names = {c["name"] for c in AdminService.get_editable_columns(User)}
        assert "role" not in names


def test_password_is_creatable_but_not_updatable(test_app):
    with test_app.app_context():
        create_names = {c["name"] for c in AdminService.get_editable_columns(User)}
        update_names = {
            c["name"] for c in AdminService.get_editable_columns(User, for_update=True)
        }
        assert "password" in create_names
        assert "password" not in update_names


def test_update_cannot_escalate_role(test_app):
    with test_app.app_context():
        user = User(email="crud-role@example.com", password="1234", role="user")
        db.session.add(user)
        db.session.commit()

        AdminService.update_record(user, {"role": "admin"}, User)
        db.session.refresh(user)
        assert user.role == "user"

        db.session.delete(user)
        db.session.commit()


def test_update_cannot_repoint_a_restricted_media_item(test_app):
    # The deny list keys on model names, so this feature does not import
    # media and a product may perfectly well install one without the other.
    # The test skips rather than inventing a dependency the code does not
    # have.
    models = pytest.importorskip("splent_io.splent_feature_media.models")
    MediaItem = models.MediaItem

    with test_app.app_context():
        item = MediaItem(
            filename="exam.pdf",
            url="/media/file/1",
            mime_type="application/pdf",
            access="restricted",
            owner_feature="courses",
            owner_ref="document:1",
        )
        db.session.add(item)
        db.session.commit()

        AdminService.update_record(
            item,
            {
                "access": "public",
                "owner_feature": "attacker",
                "owner_ref": "document:999",
                "filename": "other.pdf",
                "url": "https://evil.example/x",
                "title": "renamed",
            },
            MediaItem,
        )
        db.session.refresh(item)

        assert item.access == "restricted"
        assert item.owner_feature == "courses"
        assert item.owner_ref == "document:1"
        assert item.filename == "exam.pdf"
        assert item.url == "/media/file/1"
        # A column with no security role stays editable.
        assert item.title == "renamed"

        db.session.delete(item)
        db.session.commit()
