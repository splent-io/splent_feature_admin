"""
Integration tests for admin CRUD operations.

These tests hit a real test database.
"""

from splent_io.splent_feature_admin.services import AdminService
from splent_io.splent_feature_auth.models import User
from splent_framework.db import db


def test_count_records(test_app, admin_user):
    with test_app.app_context():
        count = AdminService.count_records(User)
        assert count >= 1


def test_get_record_by_id(test_app, admin_user):
    with test_app.app_context():
        record = AdminService.get_record(User, admin_user.id)
        assert record is not None
        assert record.email == "admin@admin.com"


def test_get_records_paginated(test_app, admin_user):
    with test_app.app_context():
        pagination = AdminService.get_records(User, page=1, per_page=10)
        assert len(pagination.items) >= 1


def test_create_and_delete_record(test_app):
    with test_app.app_context():
        record = AdminService.create_record(User, {
            "email": "test_admin_crud@example.com",
            "password": "testpass",
            "active": "1",
        })
        assert record.id is not None
        assert record.email == "test_admin_crud@example.com"

        AdminService.delete_record(record)
        assert db.session.get(User, record.id) is None


def test_update_record(test_app, admin_user):
    with test_app.app_context():
        record = db.session.get(User, admin_user.id)
        AdminService.update_record(record, {"email": "updated@admin.com"}, User)
        updated = db.session.get(User, admin_user.id)
        assert updated.email == "updated@admin.com"
