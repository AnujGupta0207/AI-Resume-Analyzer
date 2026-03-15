from flask import Flask, render_template, request, redirect, session, Response
import os
import sqlite3
import PyPDF2
import utils.advanced_ranker as ar
from database import init_db

app = Flask(__name__)
app.secret_key = "supersecurekey123"
app.config['UPLOAD_FOLDER'] = "uploads"

init_db()

if not os.path.exists("uploads"):
    os.makedirs("uploads")


# ---------------- PDF TEXT EXTRACTION ---------------- #

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["user"] = "admin"
            return redirect("/jobs")
        else:
            return render_template("login.html", error="Invalid Credentials")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- JOB LIST ---------------- #

@app.route("/jobs")
def jobs():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("hiring.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, job_description FROM jobs ORDER BY id DESC")
    jobs = cursor.fetchall()
    conn.close()

    return render_template("jobs.html", jobs=jobs)


# ---------------- CREATE JOB ---------------- #

@app.route("/create-job", methods=["GET", "POST"])
def create_job():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        job_details = request.form["job_details"]

        conn = sqlite3.connect("hiring.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO jobs (job_description) VALUES (?)", (job_details,))
        conn.commit()
        conn.close()

        return redirect("/jobs")

    return render_template("create_job.html")


# ---------------- DELETE JOB ---------------- #

@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("hiring.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE job_id=?", (job_id,))
    cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

    return redirect("/jobs")


# ---------------- UPLOAD RESUME ---------------- #

@app.route("/upload/<int:job_id>", methods=["GET", "POST"])
def upload_resume(job_id):

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        # Get job description
        conn = sqlite3.connect("hiring.db")
        cursor = conn.cursor()
        cursor.execute("SELECT job_description FROM jobs WHERE id=?", (job_id,))
        job_row = cursor.fetchone()
        conn.close()

        if not job_row:
            return "Job not found"

        job_description = job_row[0]

        # Get form data
        candidate_name = request.form.get("candidate_name")
        resume_text = request.form.get("resume_text", "")
        file = request.files.get("resume_file")

        if file and file.filename != "":
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            resume_text = extract_text_from_pdf(filepath)
            name = candidate_name if candidate_name else file.filename
        else:
            name = candidate_name if candidate_name else "Typed Resume"

        # AI Scoring
        print("USING FILE:", ar.__file__)
        result = ar.score_resume(resume_text, job_description)
        print("DEBUG RESULT:", result)

        final_score = float(result.get("final_score", 0))
        grade = result.get("grade", "N/A")
        feedback = " | ".join(result.get("feedback", ["No feedback available"]))
        recommendation = result.get("recommendation", "No recommendation")

        # Save to DB
        conn = sqlite3.connect("hiring.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO candidates (job_id, name, score, grade, feedback, recommendation)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            name,
            final_score,
            grade,
            feedback,
            recommendation
        ))

        conn.commit()
        conn.close()

        return redirect(f"/dashboard/{job_id}")

    return render_template("upload_resume.html", job_id=job_id)


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard/<int:job_id>")
def dashboard(job_id):

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("hiring.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, score, grade, feedback, recommendation
    FROM candidates
    WHERE job_id=?
    ORDER BY score DESC
    """, (job_id,))
    candidates = cursor.fetchall()

    total_candidates = len(candidates)

    if total_candidates > 0:
        scores = [c[1] for c in candidates]
        grades = [c[2] for c in candidates]

        avg_score = round(sum(scores) / total_candidates, 2)
        highest_score = max(scores)
        lowest_score = min(scores)

        grade_counts = {}
        for g in grades:
            grade_counts[g] = grade_counts.get(g, 0) + 1
    else:
        avg_score = 0
        highest_score = 0
        lowest_score = 0
        grade_counts = {}

    conn.close()

    return render_template(
        "dashboard.html",
        candidates=candidates,
        job_id=job_id,
        total_candidates=total_candidates,
        avg_score=avg_score,
        highest_score=highest_score,
        lowest_score=lowest_score,
        grade_counts=grade_counts
    )


# ---------------- EXPORT CSV ---------------- #

@app.route("/export/<int:job_id>")
def export(job_id):

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("hiring.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, score, grade, recommendation
    FROM candidates
    WHERE job_id=?
    ORDER BY score DESC
    """, (job_id,))
    candidates = cursor.fetchall()
    conn.close()

    def generate():
        yield "Name,Score,Grade,Recommendation\n"
        for c in candidates:
            yield f"{c[0]},{c[1]},{c[2]},{c[3]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=ranking.csv"}
    )


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)