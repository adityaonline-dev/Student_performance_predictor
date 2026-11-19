from datetime import datetime
import sqlite3
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from ml_model import FEATURES, MODEL_PATH, train_model, ensure_model

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "student_predictions.db"

app = Flask(__name__)
app.secret_key = "change-this-demo-secret-key"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                study_hours REAL NOT NULL,
                attendance REAL NOT NULL,
                previous_score REAL NOT NULL,
                assignment_score REAL NOT NULL,
                sleep_hours REAL NOT NULL,
                extracurricular_hours REAL NOT NULL,
                predicted_score REAL NOT NULL,
                performance TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def performance_label(score):
    if score >= 75:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Needs Improvement"
    return "At Risk"


def parse_number(form, key, label, minimum, maximum):
    raw = form.get(key, "").strip()
    if not raw:
        raise ValueError(f"{label} is required.")
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"{label} must be a number.")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")
    return value


@app.route("/", methods=["GET", "POST"])
def index():
    ensure_model()
    result = None
    form_values = {}
    if request.method == "POST":
        try:
            name = request.form.get("student_name", "").strip() or "Student"
            if len(name) > 80:
                raise ValueError("Student name must be 80 characters or fewer.")

            values = {
                "study_hours": parse_number(request.form, "study_hours", "Study hours", 0, 16),
                "attendance": parse_number(request.form, "attendance", "Attendance", 0, 100),
                "previous_score": parse_number(request.form, "previous_score", "Previous score", 0, 100),
                "assignment_score": parse_number(request.form, "assignment_score", "Assignment score", 0, 100),
                "sleep_hours": parse_number(request.form, "sleep_hours", "Sleep hours", 0, 24),
                "extracurricular_hours": parse_number(request.form, "extracurricular_hours", "Extracurricular hours", 0, 12),
            }
            form_values = {"student_name": name, **values}
            model = joblib.load(MODEL_PATH)
            sample = pd.DataFrame([values], columns=FEATURES)
            score = float(model.predict(sample)[0])
            score = round(max(0, min(100, score)), 1)
            label = performance_label(score)

            with get_db() as conn:
                cur = conn.execute("""
                    INSERT INTO predictions (
                        student_name, study_hours, attendance, previous_score,
                        assignment_score, sleep_hours, extracurricular_hours,
                        predicted_score, performance, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, values["study_hours"], values["attendance"],
                    values["previous_score"], values["assignment_score"],
                    values["sleep_hours"], values["extracurricular_hours"],
                    score, label, datetime.now().strftime("%Y-%m-%d %H:%M")
                ))
                prediction_id = cur.lastrowid

            result = {
                "id": prediction_id, "name": name, "score": score,
                "performance": label,
                "message": {
                    "Excellent": "Strong indicators. Keep your routine consistent.",
                    "Good": "A solid outlook. Regular revision may help improve further.",
                    "Needs Improvement": "Focus on attendance, practice, and a steady study plan.",
                    "At Risk": "Consider asking a teacher for support and making a realistic study plan."
                }[label]
            }
        except ValueError as exc:
            flash(str(exc), "error")
        except Exception as exc:
            app.logger.exception("Prediction failed")
            flash("Something went wrong while making the prediction. Check that the model is trained.", "error")

    with get_db() as conn:
        recent = conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC LIMIT 8"
        ).fetchall()
        totals = conn.execute("""
            SELECT COUNT(*) AS total,
                   ROUND(AVG(predicted_score), 1) AS average,
                   SUM(CASE WHEN performance = 'At Risk' THEN 1 ELSE 0 END) AS at_risk
            FROM predictions
        """).fetchone()
        distribution_rows = conn.execute("""
            SELECT performance, COUNT(*) AS count
            FROM predictions GROUP BY performance
        """).fetchall()

    distribution = {row["performance"]: row["count"] for row in distribution_rows}
    return render_template(
        "index.html", result=result, recent=recent, totals=totals,
        distribution=distribution, form_values=form_values
    )


@app.route("/history")
def history():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM predictions ORDER BY id DESC").fetchall()
    return render_template("history.html", rows=rows)


@app.route("/delete-history", methods=["POST"])
def delete_history():
    with get_db() as conn:
        conn.execute("DELETE FROM predictions")
    flash("Prediction history cleared.", "success")
    return redirect(url_for("history"))


@app.route("/api/metrics")
def api_metrics():
    metrics = ensure_model()
    return jsonify(metrics)


@app.route("/about")
def about():
    metrics = ensure_model()
    return render_template("about.html", metrics=metrics)


if __name__ == "__main__":
    init_db()
    ensure_model()
    app.run(debug=True)
