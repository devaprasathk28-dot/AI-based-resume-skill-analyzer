from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "resume-skill-analyzer-secret"

LOG_FILE = "resume_logs.txt"

# Extended role-wise expected skills
ROLE_SKILLS = {
    "ai_ds_student": {
        "label": "AI & DS Student (Placements)",
        "skills": [
            "python", "numpy", "pandas", "matplotlib", "seaborn",
            "sql", "mysql", "statistics", "probability",
            "machine learning", "supervised learning", "unsupervised learning",
            "data visualization", "data cleaning", "feature engineering",
            "git", "github", "problem solving"
        ],
    },
    "python_developer": {
        "label": "Python Developer",
        "skills": [
            "python", "oop", "object oriented programming",
            "django", "flask", "fastapi", "rest api", "api development",
            "json", "logging", "unit testing", "pytest",
            "mysql", "postgresql", "sqlite",
            "git", "github", "docker", "linux"
        ],
    },
    "data_analyst": {
        "label": "Data Analyst",
        "skills": [
            "excel", "advanced excel", "vlookup", "pivot table",
            "sql", "mysql", "postgresql",
            "pandas", "numpy", "matplotlib", "seaborn",
            "power bi", "tableau",
            "statistics", "hypothesis testing",
            "data cleaning", "data preprocessing", "dashboards"
        ],
    },
    "ml_engineer": {
        "label": "ML Engineer",
        "skills": [
            "python", "numpy", "pandas", "scikit-learn", "sklearn",
            "tensorflow", "keras", "pytorch",
            "machine learning", "deep learning", "neural networks",
            "cnn", "rnn", "lstm",
            "data preprocessing", "feature scaling",
            "model evaluation", "model deployment", "flask", "fastapi"
        ],
    },
    "web_developer": {
        "label": "Web Developer",
        "skills": [
            "html", "css", "javascript", "bootstrap",
            "react", "vue", "node", "node.js",
            "django", "flask",
            "rest api", "json", "ajax",
            "git", "github",
            "responsive design", "frontend", "backend", "full stack"
        ],
    },
    "cloud_devops": {
        "label": "Cloud / DevOps Beginner",
        "skills": [
            "linux", "bash", "shell scripting",
            "git", "github", "ci cd", "ci/cd",
            "docker", "kubernetes",
            "aws", "azure", "gcp",
            "jenkins", "terraform",
            "monitoring", "prometheus", "grafana"
        ],
    },
}

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "time management",
    "critical thinking", "problem solving", "adaptability",
    "creativity", "collaboration", "self motivation", "presentation"
]


def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("==== Resume Skill Analyzer Logs (Web Version) ====\n\n")


def analyze_resume_text(resume_text: str, role_key: str):
    text = (resume_text or "").lower()
    role_info = ROLE_SKILLS.get(role_key, ROLE_SKILLS["ai_ds_student"])
    expected_skills = role_info["skills"]

    # Role-specific matches
    found_for_role = sorted({s for s in expected_skills if s in text})
    missing_for_role = sorted([s for s in expected_skills if s not in found_for_role])

    # All tech skills for extra detection
    all_hard_skills = sorted({s for info in ROLE_SKILLS.values() for s in info["skills"]})
    found_hard = sorted({s for s in all_hard_skills if s in text})

    # Soft skills
    found_soft = sorted({s for s in SOFT_SKILLS if s in text})
    missing_soft = sorted([s for s in SOFT_SKILLS if s not in found_soft])

    score = 0
    if expected_skills:
        score = round(len(found_for_role) / len(expected_skills) * 100)

    summary = {
        "role_key": role_key,
        "role_label": role_info["label"],
        "expected_skills": expected_skills,
        "found_for_role": found_for_role,
        "missing_for_role": missing_for_role,
        "found_hard": found_hard,
        "found_soft": found_soft,
        "missing_soft": missing_soft,
        "score": score,
    }
    return summary


def append_log(name: str, summary: dict):
    init_log_file()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("==============================================")
    lines.append(f"Name       : {name}")
    lines.append(f"Role       : {summary['role_label']}")
    lines.append(f"Analyzed on: {now}")
    lines.append(f"Skill Score: {summary['score']}%")

    lines.append("Matched Skills for Role:")
    if summary["found_for_role"]:
        for s in summary["found_for_role"]:
            lines.append(f"  - {s}")
    else:
        lines.append("  (none)")

    lines.append("Missing Skills for Role:")
    if summary["missing_for_role"]:
            lines.append(f"  - {s}")
    else:
        lines.append("  (none)")

    lines.append("Soft Skills Mentioned:")
    if summary["found_soft"]:
        for s in summary["found_soft"]:
            lines.append(f"  - {s}")
    else:
        lines.append("  (none)")

    lines.append("==============================================\n")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", roles=ROLE_SKILLS)


@app.route("/analyze", methods=["POST"])
def analyze():
    name = (request.form.get("name") or "").strip()
    role_key = (request.form.get("role") or "ai_ds_student").strip()
    resume_text = (request.form.get("resume_text") or "").strip()

    if not name:
        flash("Please enter your name.")
        return redirect(url_for("index"))
    if not resume_text:
        flash("Please paste your resume text for analysis.")
        return redirect(url_for("index"))

    summary = analyze_resume_text(resume_text, role_key)
    append_log(name, summary)

    return render_template(
        "result.html",
        name=name,
        resume_text=resume_text,
        summary=summary,
    )


@app.route("/logs", methods=["GET"])
def logs():
    init_log_file()
    if not os.path.exists(LOG_FILE):
        content = "No logs found yet."
    else:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            content = data or "No logs found yet."
    return render_template("logs.html", logs=content)


if __name__ == "__main__":
    init_log_file()
    # Simple to run in lab:
    app.run(debug=True)
    # If you want WSGI in future:
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5000)
