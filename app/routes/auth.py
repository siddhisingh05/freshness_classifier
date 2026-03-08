from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models.database import get_db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        flash("Both fields are required.")
        return redirect(request.url)

    if len(username) < 3:
        flash("Username must be at least 3 characters.")
        return redirect(request.url)

    if len(password) < 6:
        flash("Password must be at least 6 characters.")
        return redirect(request.url)

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        flash("Username already taken.")
        return redirect(request.url)

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    db.commit()

    flash("Account created. Please log in.")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        flash("Both fields are required.")
        return redirect(request.url)

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if not user or not bcrypt.check_password_hash(user["password"], password):
        flash("Invalid username or password.")
        return redirect(request.url)

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("predict.upload"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
