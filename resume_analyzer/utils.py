import fitz
import docx

SKILL_CATEGORIES = {
    "web_development": ["html", "css", "javascript", "bootstrap", "react", "django"],
    "python_development": ["python", "django", "flask", "api", "backend"],
    "machine_learning": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "nlp"],
    "data_analyst": ["python", "sql", "data analysis", "pandas", "excel", "power bi"]
}


def extract_text_from_pdf(path):
    text = ""
    doc = fitz.open(path)
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text(path):
    if path.endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif path.endswith(".docx"):
        return extract_text_from_docx(path)
    return ""


def extract_skills(text):
    text = text.lower()
    skills = []

    all_skills = []
    for v in SKILL_CATEGORIES.values():
        all_skills.extend(v)

    for skill in all_skills:
        if skill in text:
            skills.append(skill)

    return list(set(skills))


def detect_domain(skills):
    scores = {}

    for domain, keywords in SKILL_CATEGORIES.items():
        scores[domain] = len(set(skills) & set(keywords))

    if all(v == 0 for v in scores.values()):
        return "general"

    return max(scores, key=scores.get)


def calculate_ats_score(skills, domain):
    if domain == "general":
        return 0

    domain_skills = SKILL_CATEGORIES[domain]
    return int((len(set(skills) & set(domain_skills)) / len(domain_skills)) * 100)


def get_missing_skills(found, domain):
    if domain == "general":
        return []

    return list(set(SKILL_CATEGORIES[domain]) - set(found))


def generate_suggestions(skills, missing, domain, ats):

    suggestions = []

    if ats >= 80:
        suggestions.append("Your resume is strong and well optimized for ATS systems.")
    elif ats >= 50:
        suggestions.append("Your resume is good but can be improved.")
    else:
        suggestions.append("Your resume needs improvement.")

    for m in missing:
        suggestions.append(f"Consider adding skill: {m}")

    if domain == "web_development":
        suggestions.append("Add React/Django projects.")
    elif domain == "machine_learning":
        suggestions.append("Add ML projects with real datasets.")
    elif domain == "data_analyst":
        suggestions.append("Include SQL dashboards or Power BI projects.")
    elif domain == "python_development":
        suggestions.append("Build API/backend projects.")

    return suggestions