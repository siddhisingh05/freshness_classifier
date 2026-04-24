import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from ..utils.inference import predict
from ..models.database import get_db
from functools import wraps
from PIL import Image

predict_bp = Blueprint("predict", __name__)

allowed_ext = {"png", "jpg", "jpeg", "webp"}


def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if "user_id" not in session:
            flash("Login first to continue")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return check_login


def is_valid_file(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in allowed_ext


@predict_bp.route("/predict", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("predict.html")

    img = request.files.get("image")

    # 1. Empty file check
    if not img or img.filename == "":
        flash("Please select an image")
        return redirect(request.url)

    # 2. Extension check
    if not is_valid_file(img.filename):
        flash("Only PNG, JPG, JPEG, WEBP allowed")
        return redirect(request.url)

    # 3. File size check (extra safety)
    if request.content_length and request.content_length > 5 * 1024 * 1024:
        flash("File too large (max 5MB)")
        return redirect(request.url)

    # 4. Save file
    ext = img.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    try:
        img.save(path)
    except Exception:
        flash("Error saving file")
        return redirect(request.url)

    # 5. Check if it's a valid image
    try:
        Image.open(path).verify()
    except Exception:
        os.remove(path)
        flash("Invalid or corrupted image")
        return redirect(request.url)

    # 6. Prediction
    try:
        result = predict(path)
    except Exception:
        flash("Error while processing image")
        return redirect(request.url)

    # 7. Save to DB
    db = get_db()
    db.execute(
        "INSERT INTO predictions (filename, original_name, label, display_label, confidence) VALUES (?, ?, ?, ?, ?)",
        (filename, secure_filename(img.filename), result["label"], result["display_label"], result["freshness_score"]),
    )
    db.commit()

    return render_template(
        "result.html",
        filename=filename,
        original=secure_filename(img.filename),
        result=result,
    )