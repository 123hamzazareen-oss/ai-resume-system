from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(
    resume_text,
    job_text,
    resume_skills
):
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
    resume_skills = [
        s.strip().lower()
        for s in resume_skills.split(",")
        if s.strip()
    ]
    job_text = job_text.lower()
    matched = 0
    matched_skills = []

    for skill in resume_skills:
        if skill in job_text:
            matched += 1
            matched_skills.append(skill)

    if len(resume_skills) == 0:
        skill_score = 0

    else:
        skill_score = (
            matched / len(resume_skills)
        ) * 100

    final_score = (
        (0.60 * skill_score) +
        (0.40 * text_score)
    )

    return round(final_score, 2)

def classify_match(score):
    if score >= 75:
        return "High Match"

    elif score >= 50:
        return "Medium Match"

    return "Low Match"
