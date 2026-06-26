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

import re

# Master taxonomy combining preset roles and extra modern technologies
MASTER_TAXONOMY = sorted(list(set(
    [s for info in ROLE_SKILLS.values() for s in info["skills"]] +
    SOFT_SKILLS +
    [
        "typescript", "java", "c++", "c#", "go", "golang", "rust", "php", "ruby", "swift", "kotlin",
        "flutter", "react native", "agile", "scrum", "graphql", "mongodb", "redis", "elasticsearch",
        "kafka", "rabbitmq", "nginx", "gitlab", "github actions", "ansible", "unix", "devops",
        "microservices", "serverless", "next.js", "nextjs", "angular", "node.js", "nodejs",
        "express", "spring boot", "tailwind", "sass", "less", "redux", "webpack", "npm", "yarn"
    ]
)))


def init_log_file():
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("==== Resume Skill Analyzer Logs (Web Version) ====\n\n")
    except OSError:
        pass # Ignore filesystem errors in serverless execution


def extract_skills_from_jd(jd_text: str):
    text = (jd_text or "").lower()
    found_skills = []
    for s in MASTER_TAXONOMY:
        if len(s) <= 3:
            # Word boundary search for short strings (avoid matching 'go' in 'good')
            pattern = rf"\b{re.escape(s)}\b"
            if re.search(pattern, text):
                found_skills.append(s)
        else:
            if s in text:
                found_skills.append(s)
    return sorted(list(set(found_skills)))


def analyze_resume_text(resume_text: str, role_key: str, jd_text: str = None):
    text = (resume_text or "").lower()
    
    if jd_text:
        # Jobscan Custom JD Mode
        expected_skills = extract_skills_from_jd(jd_text)
        role_label = "Custom Job Description (Jobscan Mode)"
        if not expected_skills:
            # Fallback expected skills if none matched the taxonomy
            expected_skills = ["python", "sql", "git", "communication", "problem-solving"]
            role_label = "Custom Job Description (Fallback Preset)"
    else:
        # Preset Mode
        role_info = ROLE_SKILLS.get(role_key, ROLE_SKILLS["ai_ds_student"])
        expected_skills = role_info["skills"]
        role_label = role_info["label"]

    # Match expected skills
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

    # Suitability & ATS Pass Chance
    if score >= 80:
        suitability_status = "Excellent Match"
        suitability_desc = "Highly Suitable - Your resume demonstrates outstanding alignment with the job requirements."
        ats_verdict = "Strong Pass"
        ats_desc = "Highly likely to clear automated parsing rules. Key skill phrases are well covered."
    elif score >= 50:
        suitability_status = "Suitable"
        suitability_desc = "Suitable with Tailoring - You cover core keywords, but optimizing the missing skills will maximize response rates."
        ats_verdict = "Borderline"
        ats_desc = "Moderate pass probability. Key skill gaps might trigger automatic screening filters."
    else:
        suitability_status = "Not Yet Suitable"
        suitability_desc = "Low Alignment - Significant skill gaps detected. You should acquire or highlight the missing skills to match this JD."
        ats_verdict = "High Risk"
        ats_desc = "Likely to be filtered out by automated ATS keywords check. Needs immediate tailoring."

    summary = {
        "role_key": role_key,
        "role_label": role_label,
        "expected_skills": expected_skills,
        "found_for_role": found_for_role,
        "missing_for_role": missing_for_role,
        "found_hard": found_hard,
        "found_soft": found_soft,
        "missing_soft": missing_soft,
        "score": score,
        "suitability_status": suitability_status,
        "suitability_desc": suitability_desc,
        "ats_verdict": ats_verdict,
        "ats_desc": ats_desc,
        "is_custom": bool(jd_text)
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
        for s in summary["missing_for_role"]:
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

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except OSError:
        pass # Ignore file writes on read-only environments


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", roles=ROLE_SKILLS)


@app.route("/analyze", methods=["POST"])
def analyze():
    name = (request.form.get("name") or "").strip()
    analysis_method = (request.form.get("analysis_method") or "preset").strip()
    role_key = (request.form.get("role") or "ai_ds_student").strip()
    job_description = (request.form.get("job_description") or "").strip()
    resume_text = (request.form.get("resume_text") or "").strip()

    if not name:
        flash("Please enter your name.")
        return redirect(url_for("index"))
    if not resume_text:
        flash("Please paste your resume text for analysis.")
        return redirect(url_for("index"))
    if analysis_method == "custom" and not job_description:
        flash("Please paste the Job Description to perform a Jobscan analysis.")
        return redirect(url_for("index"))

    if analysis_method == "custom":
        summary = analyze_resume_text(resume_text, role_key, jd_text=job_description)
    else:
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
    content = "No logs found yet."
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = f.read().strip()
                content = data or "No logs found yet."
        except OSError:
            content = "System logs are unavailable in this server environment."
    return render_template("logs.html", logs=content)


if __name__ == "__main__":
    init_log_file()
    # Simple to run in lab:
    app.run(debug=True)
    # If you want WSGI in future:
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5000)
