# AI-based-resume-skill-analyzer
AI-Based Resume Skill Analyzer is a Python web app that evaluates a resume against a selected job role using smart keyword matching. It displays matched and missing technical and soft skills, calculates a match score, and saves results using file handling. Built with Flask.
## 🚀 Features

- ✅ Role-based resume analysis
- ✅ Calculates **Skill Match Percentage**
- ✅ Detects:
  - Matched technical skills
  - Missing technical skills
  - Soft skills mentioned
  - Soft skills missing
- ✅ Clean & responsive web interface
- ✅ Resume analysis logs stored using Python file handling
- ✅ Multiple roles supported:
  - AI & DS Student (Placements)
  - Python Developer
  - Data Analyst
  - ML Engineer
  - Web Developer
  - Cloud / DevOps Beginner

---

## 🛠️ Technologies Used

- **Python 3**
- **Flask (Web Framework)**
- **HTML & CSS**
- **Keyword-based NLP Logic**
- **File Handling (`resume_logs.txt`)**

---

## 📁 Project Structure

resume_skill_analyzer_web/
│
├── app.py
├── resume_logs.txt
└── templates/
├── base.html
├── index.html
├── result.html
└── logs.html
