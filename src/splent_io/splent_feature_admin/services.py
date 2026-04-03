from sqlalchemy import inspect as sa_inspect

from splent_framework.db import db


# Column types to skip in list views (too verbose for table display)
_SKIP_TYPES_IN_LIST = {"TEXT", "BLOB", "JSON", "LONGTEXT", "MEDIUMTEXT"}

# Maximum columns shown in the list view
_MAX_LIST_COLUMNS = 7


class AdminService:
    """Service for auto-generated CRUD operations on all registered models."""

    # ── Model discovery ──────────────────────────────────────────────────

    @staticmethod
    def get_models() -> dict[str, type]:
        """Return all registered SQLAlchemy model classes keyed by name."""
        return {cls.__name__: cls for cls in db.Model.__subclasses__()}

    @staticmethod
    def get_model(name: str) -> type | None:
        """Return a single model class by name, or None."""
        models = AdminService.get_models()
        return models.get(name)

    # ── Column introspection ─────────────────────────────────────────────

    @staticmethod
    def get_columns(model: type) -> list[dict]:
        """Return column metadata for a model via SQLAlchemy inspect."""
        mapper = sa_inspect(model)
        cols = []
        for col in mapper.columns:
            fk = None
            if col.foreign_keys:
                fk = str(list(col.foreign_keys)[0].target_fullname)
            cols.append({
                "name": col.name,
                "type": str(col.type),
                "primary_key": col.primary_key,
                "nullable": col.nullable,
                "foreign_key": fk,
            })
        return cols

    @staticmethod
    def get_list_columns(model: type) -> list[dict]:
        """Return columns suitable for the list view (filtered and capped)."""
        cols = AdminService.get_columns(model)
        filtered = [
            c for c in cols
            if c["type"].upper().split("(")[0] not in _SKIP_TYPES_IN_LIST
        ]
        return filtered[:_MAX_LIST_COLUMNS]

    @staticmethod
    def get_editable_columns(model: type) -> list[dict]:
        """Return columns that can be edited (excludes primary keys)."""
        return [c for c in AdminService.get_columns(model) if not c["primary_key"]]

    # ── CRUD operations ──────────────────────────────────────────────────

    @staticmethod
    def get_record(model: type, record_id: int):
        """Fetch a single record by primary key."""
        return db.session.get(model, record_id)

    @staticmethod
    def get_records(model: type, page: int = 1, per_page: int = 20):
        """Return a paginated query for the given model."""
        return model.query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def count_records(model: type) -> int:
        """Return the total number of records for a model."""
        return model.query.count()

    @staticmethod
    def create_record(model: type, form_data: dict):
        """Create a new record from form data."""
        editable = {c["name"] for c in AdminService.get_editable_columns(model)}
        nullable = {c["name"] for c in AdminService.get_columns(model) if c["nullable"]}

        data = {}
        for key, value in form_data.items():
            if key in editable:
                if value == "" and key in nullable:
                    data[key] = None
                else:
                    data[key] = value

        record = model(**data)
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def update_record(record, form_data: dict, model: type):
        """Update an existing record from form data."""
        editable = {c["name"] for c in AdminService.get_editable_columns(model)}
        nullable = {c["name"] for c in AdminService.get_columns(model) if c["nullable"]}

        for key, value in form_data.items():
            if key in editable:
                if value == "" and key in nullable:
                    setattr(record, key, None)
                else:
                    setattr(record, key, value)

        db.session.commit()

    @staticmethod
    def delete_record(record):
        """Delete a record from the database."""
        db.session.delete(record)
        db.session.commit()
