from flask import flash, render_template, redirect, url_for, request

from splent_framework.decorators.decorators import role_required

from splent_io.splent_feature_admin import admin_bp
from splent_io.splent_feature_admin.services import AdminService

# The generic CRUD reaches every model in the product, so it is the most
# privileged screen there is. The auth migration backfills pre-existing
# accounts to admin, so products that upgrade keep the access they had.
ADMIN_ROLES = ("admin",)


@admin_bp.route("/admin", methods=["GET"])
@role_required(*ADMIN_ROLES)
def dashboard():
    models = AdminService.get_models()
    model_stats = []
    for name, cls in sorted(models.items()):
        model_stats.append(
            {
                "name": name,
                "count": AdminService.count_records(cls),
                "columns": len(AdminService.get_columns(cls)),
            }
        )
    return render_template("admin/dashboard.html", models=model_stats)


@admin_bp.route("/admin/<model_name>", methods=["GET"])
@role_required(*ADMIN_ROLES)
def model_list(model_name):
    model = AdminService.get_model(model_name)
    if model is None:
        flash(f"Model '{model_name}' not found.", "danger")
        return redirect(url_for("admin.dashboard"))

    page = request.args.get("page", 1, type=int)
    pagination = AdminService.get_records(model, page=page)
    columns = AdminService.get_list_columns(model)

    return render_template(
        "admin/list.html",
        model_name=model_name,
        columns=columns,
        pagination=pagination,
        records=pagination.items,
    )


@admin_bp.route("/admin/<model_name>/create", methods=["GET", "POST"])
@role_required(*ADMIN_ROLES)
def create(model_name):
    model = AdminService.get_model(model_name)
    if model is None:
        flash(f"Model '{model_name}' not found.", "danger")
        return redirect(url_for("admin.dashboard"))

    columns = AdminService.get_editable_columns(model)

    if request.method == "POST":
        AdminService.create_record(model, request.form.to_dict())
        flash(f"{model_name} created successfully.", "success")
        return redirect(url_for("admin.model_list", model_name=model_name))

    return render_template(
        "admin/form.html",
        model_name=model_name,
        columns=columns,
        record=None,
        action="Create",
    )


@admin_bp.route("/admin/<model_name>/<int:id>", methods=["GET", "POST"])
@role_required(*ADMIN_ROLES)
def edit(model_name, id):
    model = AdminService.get_model(model_name)
    if model is None:
        flash(f"Model '{model_name}' not found.", "danger")
        return redirect(url_for("admin.dashboard"))

    record = AdminService.get_record(model, id)
    if record is None:
        flash(f"{model_name} with id {id} not found.", "danger")
        return redirect(url_for("admin.model_list", model_name=model_name))

    columns = AdminService.get_editable_columns(model, for_update=True)

    if request.method == "POST":
        AdminService.update_record(record, request.form.to_dict(), model)
        flash(f"{model_name} updated successfully.", "success")
        return redirect(url_for("admin.model_list", model_name=model_name))

    return render_template(
        "admin/form.html",
        model_name=model_name,
        columns=columns,
        record=record,
        action="Edit",
    )


@admin_bp.route("/admin/<model_name>/<int:id>/delete", methods=["GET", "POST"])
@role_required(*ADMIN_ROLES)
def delete(model_name, id):
    model = AdminService.get_model(model_name)
    if model is None:
        flash(f"Model '{model_name}' not found.", "danger")
        return redirect(url_for("admin.dashboard"))

    record = AdminService.get_record(model, id)
    if record is None:
        flash(f"{model_name} with id {id} not found.", "danger")
        return redirect(url_for("admin.model_list", model_name=model_name))

    if request.method == "POST":
        AdminService.delete_record(record)
        flash(f"{model_name} deleted successfully.", "success")
        return redirect(url_for("admin.model_list", model_name=model_name))

    columns = AdminService.get_columns(model)

    return render_template(
        "admin/delete.html",
        model_name=model_name,
        columns=columns,
        record=record,
    )
