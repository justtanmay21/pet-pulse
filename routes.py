import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    current_app, flash, send_from_directory, abort
)
from werkzeug.utils import secure_filename

import models

main_blueprint = Blueprint("main", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _allowed(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def _save_upload(file_storage, folder, allowed_extensions):
    """Save an uploaded file with a collision-proof name; return the stored filename or None."""
    if not file_storage or file_storage.filename == "":
        return None
    filename = secure_filename(file_storage.filename)
    if not _allowed(filename, allowed_extensions):
        flash(f"'{filename}' is not an allowed file type.", "danger")
        return None
    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, unique_name))
    return unique_name


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@main_blueprint.route("/")
def index():
    pets = models.fetch_all_pets()
    appointments = models.fetch_all_appointments()
    reports = models.fetch_all_reports()
    pet_insurance = models.fetch_pet_insurance()
    policies = {p["id"]: p for p in models.fetch_all_policies()}

    # Build a quick pet_id -> [policy, ...] map for the template
    policies_by_pet = {}
    for link in pet_insurance:
        policies_by_pet.setdefault(link["pet_id"], []).append(policies.get(link["policy_id"]))

    # Build a quick pet_id -> [appointment, ...] map
    appts_by_pet = {}
    for a in appointments:
        appts_by_pet.setdefault(a["pet_id"], []).append(a)

    # Build a quick pet_id -> [report, ...] map
    reports_by_pet = {}
    for r in reports:
        reports_by_pet.setdefault(r["pet_id"], []).append(r)

    return render_template(
        "index.html",
        pets=pets,
        policies_by_pet=policies_by_pet,
        appts_by_pet=appts_by_pet,
        reports_by_pet=reports_by_pet,
    )


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

@main_blueprint.route("/add_pet", methods=["GET", "POST"])
def add_pet():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        animal = request.form.get("animal", "").strip()
        age = request.form.get("age", "").strip()
        allergies = request.form.get("allergies", "").strip()
        owner = request.form.get("owner", "").strip()

        if not name or not animal:
            flash("Pet name and animal/breed are required.", "danger")
            return redirect(url_for("main.add_pet"))

        image_file = _save_upload(
            request.files.get("file"),
            current_app.config["PET_IMAGE_FOLDER"],
            current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
        )

        models.add_pet(name, animal, age, allergies, owner, image_file)
        flash(f"{name} was added to Pet Pulse.", "success")
        return redirect(url_for("main.index"))

    return render_template("add_pet.html")


@main_blueprint.route("/update_pet/<int:pet_id>", methods=["GET", "POST"])
def update_pet(pet_id):
    pet = models.fetch_pet(pet_id)
    if pet is None:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        animal = request.form.get("animal", "").strip()
        age = request.form.get("age", "").strip()
        allergies = request.form.get("allergies", "").strip()
        owner = request.form.get("owner", "").strip()

        image_file = _save_upload(
            request.files.get("file"),
            current_app.config["PET_IMAGE_FOLDER"],
            current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
        )

        models.update_pet(pet_id, name, animal, age, allergies, owner, image_file)
        flash(f"{name}'s profile was updated.", "success")
        return redirect(url_for("main.index"))

    return render_template("update_pet.html", pet=pet)


@main_blueprint.route("/delete_pet/<int:pet_id>", methods=["POST"])
def delete_pet(pet_id):
    pet = models.fetch_pet(pet_id)
    if pet is None:
        abort(404)
    models.delete_pet(pet_id)
    flash(f"{pet['name']} was removed.", "info")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@main_blueprint.route("/upload_report", methods=["GET", "POST"])
def upload_report():
    pets = models.fetch_all_pets()

    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        report_name = request.form.get("report_name", "").strip()

        if not pet_id or not report_name:
            flash("Please choose a pet and name the report.", "danger")
            return redirect(url_for("main.upload_report"))

        report_file = _save_upload(
            request.files.get("report_file"),
            current_app.config["REPORT_FOLDER"],
            current_app.config["ALLOWED_REPORT_EXTENSIONS"],
        )
        if not report_file:
            flash("Please attach a valid report file (pdf, jpg, png, doc, docx).", "danger")
            return redirect(url_for("main.upload_report"))

        models.add_report(pet_id, report_name, report_file)
        flash("Report uploaded and linked to the pet.", "success")
        return redirect(url_for("main.index"))

    return render_template("upload_report.html", pets=pets)


@main_blueprint.route("/display_report/<path:filename>")
def display_report(filename):
    safe_filename = secure_filename(filename)
    try:
        return send_from_directory(
            current_app.config["REPORT_FOLDER"], safe_filename, as_attachment=False
        )
    except FileNotFoundError:
        abort(404)


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

@main_blueprint.route("/schedule_appointment", methods=["GET", "POST"])
def schedule_appointment():
    pets = models.fetch_all_pets()

    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        date = request.form.get("date")
        description = request.form.get("description", "").strip()
        virtual = request.form.get("virtual") == "on"

        if not pet_id or not date:
            flash("Please choose a pet and an appointment date/time.", "danger")
            return redirect(url_for("main.schedule_appointment"))

        models.add_appointment(pet_id, date, description, virtual)
        flash("Appointment scheduled.", "success")
        return redirect(url_for("main.index"))

    return render_template("schedule_appointment.html", pets=pets)


# ---------------------------------------------------------------------------
# Emergency contacts
# ---------------------------------------------------------------------------

@main_blueprint.route("/emergency_contacts")
def emergency_contacts():
    contacts = models.fetch_emergency_contacts()
    return render_template("emergency_contacts.html", contacts=contacts)


# ---------------------------------------------------------------------------
# Insurance
# ---------------------------------------------------------------------------

@main_blueprint.route("/insurance", methods=["GET", "POST"])
def insurance():
    pets = models.fetch_all_pets()
    policies = models.fetch_all_policies()

    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        policy_id = request.form.get("policy_id")
        if pet_id and policy_id:
            models.add_pet_policy(pet_id, policy_id)
            flash("Policy linked to pet.", "success")
        return redirect(url_for("main.insurance"))

    pet_policies = {}
    for pet in pets:
        pet_policies[pet["id"]] = models.fetch_pet_policies(pet["id"])

    return render_template(
        "insurance.html", pets=pets, policies=policies, pet_policies=pet_policies
    )
