import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(
    resume_text,
    job_text,
    resume_skills
):
    resume_text = (resume_text or "").strip()
    job_text = (job_text or "").strip()

    if not resume_text or not job_text:
        text_score = 0
    else:
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000
            )
            tfidf_matrix = vectorizer.fit_transform([
                resume_text,
                job_text
            ])
            similarity = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2]
            )[0][0]
            text_score = similarity * 100
        except Exception:
            text_score = 0

    resume_skills_list = [
        s.strip().lower()
        for s in (resume_skills or "").split(",")
        if s.strip()
    ]
    job_text_lower = job_text.lower()
    matched = 0
    matched_skills = []

    for skill in resume_skills_list:
        escaped = re.escape(skill)
        if re.search(r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])', job_text_lower):
            matched += 1
            matched_skills.append(skill)

    if len(resume_skills_list) == 0:
        skill_score = 0
    else:
        skill_score = (
            matched / len(resume_skills_list)
        ) * 100

    final_score = (
        (0.60 * skill_score) +
        (0.40 * text_score)
    )

    return round(final_score, 2)

def classify_match(score):
    if score >= 70:
        return "High Match"
    elif score >= 45:
        return "Medium Match"
    return "Low Match"
