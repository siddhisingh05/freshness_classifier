from flask import Blueprint, render_template, request
from ..models.database import get_db

history_bp = Blueprint("history", __name__)

PER_PAGE = 20


@history_bp.route("/history")
def history():
    db = get_db()
    page = max(1, request.args.get("page", 1, type=int))
    label_filter = request.args.get("label", "")

    base_query = "FROM predictions"
    params = []

    if label_filter in ("fresh", "stale"):
        base_query += " WHERE label = ?"
        params.append(label_filter)

    total = db.execute(f"SELECT COUNT(*) {base_query}", params).fetchone()[0]
    offset = (page - 1) * PER_PAGE

    rows = db.execute(
        f"SELECT * {base_query} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [PER_PAGE, offset],
    ).fetchall()

    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

    return render_template(
        "history.html",
        rows=rows,
        page=page,
        total_pages=total_pages,
        label_filter=label_filter,
        total=total,
    )
