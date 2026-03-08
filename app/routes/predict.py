import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from ..utils.inference import predict
from ..models.database import get_db
from functools import wraps

predict_bp = Blueprint("predict", __name__)

ALLOWED = {"png", "jpg", "jpeg", "webp"}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to classify images.")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@predict_bp.route("/predict", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("predict.html")

    file = request.files.get("image")
    if not file or file.filename == "":
        flash("No file selected.")
        return redirect(request.url)

    if not _allowed(file.filename):
        flash("Only PNG, JPG, JPEG, and WEBP files are accepted.")
        return redirect(request.url)

    ext = file.filename.rsplit(".", 1)[1].lower()
    saved_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], saved_name)
    file.save(save_path)

    result = predict(save_path)

    db = get_db()
    db.execute(
        "INSERT INTO predictions (filename, original_name, label, display_label, confidence) VALUES (?, ?, ?, ?, ?)",
        (saved_name, secure_filename(file.filename), result["label"], result["display_label"], result["freshness_score"]),
    )
    db.commit()

    return render_template(
        "result.html",
        filename=saved_name,
        original=secure_filename(file.filename),
        result=result,
    )
