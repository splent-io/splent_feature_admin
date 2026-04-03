from unittest.mock import MagicMock, patch
from splent_io.splent_feature_admin.services import AdminService


def test_get_models_returns_dict():
    with patch.object(AdminService, "get_models") as mock_get:
        mock_model = MagicMock()
        mock_get.return_value = {"FakeModel": mock_model}

        result = AdminService.get_models()

        assert "FakeModel" in result
        assert result["FakeModel"] is mock_model


def test_get_model_returns_none_for_unknown():
    with patch.object(AdminService, "get_models", return_value={}):
        result = AdminService.get_model("NonExistent")
        assert result is None


@patch("splent_io.splent_feature_admin.services.sa_inspect")
def test_get_columns_returns_metadata(mock_inspect):
    mock_col = MagicMock()
    mock_col.name = "id"
    mock_col.type = MagicMock(__str__=lambda self: "INTEGER")
    mock_col.primary_key = True
    mock_col.nullable = False
    mock_col.foreign_keys = set()

    mock_mapper = MagicMock()
    mock_mapper.columns = [mock_col]
    mock_inspect.return_value = mock_mapper

    model = MagicMock()
    result = AdminService.get_columns(model)

    assert len(result) == 1
    assert result[0]["name"] == "id"
    assert result[0]["primary_key"] is True


@patch("splent_io.splent_feature_admin.services.sa_inspect")
def test_get_editable_columns_excludes_pk(mock_inspect):
    pk_col = MagicMock()
    pk_col.name = "id"
    pk_col.type = MagicMock(__str__=lambda self: "INTEGER")
    pk_col.primary_key = True
    pk_col.nullable = False
    pk_col.foreign_keys = set()

    data_col = MagicMock()
    data_col.name = "email"
    data_col.type = MagicMock(__str__=lambda self: "VARCHAR(256)")
    data_col.primary_key = False
    data_col.nullable = False
    data_col.foreign_keys = set()

    mock_mapper = MagicMock()
    mock_mapper.columns = [pk_col, data_col]
    mock_inspect.return_value = mock_mapper

    model = MagicMock()
    result = AdminService.get_editable_columns(model)

    assert len(result) == 1
    assert result[0]["name"] == "email"
