from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models.database import get_db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
auth_bp = Blueprint("auth", __name__)

questions_list = [
    "What is the name of your first pet?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
    "What is your favourite food?",
    "What city were you born in?",
]


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html", questions=questions_list)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    ques = request.form.get("secret_question", "").strip()
    ans = request.form.get("secret_answer", "").strip().lower()

    if not username or not password or not ques or not ans:
        flash("Please fill all fields.")
        return redirect(request.url)

    if len(username) < 3:
        flash("Username too short.")
        return redirect(request.url)

    if len(password) < 6:
        flash("Password must be at least 6 characters.")
        return redirect(request.url)

    db = get_db()

    existing_user = db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()

    if existing_user:
        flash("Username already exists.")
        return redirect(request.url)

    hashed_pass = bcrypt.generate_password_hash(password).decode("utf-8")

    db.execute(
        "INSERT INTO users (username, password, secret_question, secret_answer) VALUES (?, ?, ?, ?)",
        (username, hashed_pass, ques, ans)
    )
    db.commit()

    flash("Account created successfully.")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        flash("Enter both username and password.")
        return redirect(request.url)

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user or not bcrypt.check_password_hash(user["password"], password):
        flash("Wrong username or password.")
        return redirect(request.url)

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return redirect(url_for("predict.upload"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("auth/forgot_password.html")

    username = request.form.get("username", "").strip()

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user:
        flash("User not found.")
        return redirect(request.url)

    session["reset_user"] = user["id"]

    return redirect(
        url_for("auth.verify_answer", question=user["secret_question"])
    )


@auth_bp.route("/verify-answer", methods=["GET", "POST"])
def verify_answer():
    if "reset_user" not in session:
        return redirect(url_for("auth.forgot_password"))

    ques = request.args.get("question", "")

    if request.method == "GET":
        return render_template("auth/verify_answer.html", question=ques)

    ans = request.form.get("secret_answer", "").strip().lower()

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (session["reset_user"],)
    ).fetchone()

    if not user or user["secret_answer"] != ans:
        flash("Answer is incorrect.")
        return redirect(
            url_for("auth.verify_answer", question=user["secret_question"])
        )

    session["verified"] = True
    return redirect(url_for("auth.reset_password"))


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_user" not in session or not session.get("verified"):
        return redirect(url_for("auth.forgot_password"))

    if request.method == "GET":
        return render_template("auth/reset_password.html")

    password = request.form.get("password", "").strip()
    confirm = request.form.get("confirm_password", "").strip()

    if len(password) < 6:
        flash("Password too short.")
        return redirect(request.url)

    if password != confirm:
        flash("Passwords do not match.")
        return redirect(request.url)

    hashed_pass = bcrypt.generate_password_hash(password).decode("utf-8")

    db = get_db()
    db.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (hashed_pass, session["reset_user"])
    )
    db.commit()

    session.pop("reset_user", None)
    session.pop("verified", None)

    flash("Password changed successfully.")
    return redirect(url_for("auth.login"))