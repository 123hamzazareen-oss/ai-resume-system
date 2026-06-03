import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MatchEngine:
    def __init__(self, resume_text, skills, domain):
        self.resume_text = (resume_text or "").lower()
        self.skills = [s.lower().strip() for s in skills]
        self.domain = domain.lower()
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000
        )
        self.domain_keywords = {
            "web_development": [
                "django",
                "react",
                "javascript",
                "frontend",
                "backend",
                "web developer",
                "full stack"
            ],
            "python_development": [
                "python",
                "django",
                "flask",
                "fastapi",
                "backend",
                "api",
                "rest api",
                "software engineer",
                "backend developer"
            ],
            "machine_learning": [
                "machine learning",
                "deep learning",
                "tensorflow",
                "pytorch",
                "nlp",
                "ai",
                "data science",
                "computer vision"
            ],
            "data_analyst": [
                "sql",
                "pandas",
                "excel",
                "power bi",
                "analytics",
                "dashboard",
                "business intelligence"
            ]
        }
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9+#. ]", " ", text)

        return text

    def compute_score(self, job_text):
        job_text = self.clean_text(job_text)
        try:
            vectors = self.vectorizer.fit_transform([
                self.resume_text,
                job_text
            ])
            similarity = cosine_similarity(
                vectors[0:1],
                vectors[1:2]
            )[0][0]
            text_score = similarity * 100

        except Exception:
            text_score = 0

        matched_skills = []
        matched_count = 0

        for skill in self.skills:
            if skill in job_text:
                matched_skills.append(skill)
                matched_count += 1

        # percentage of skills matched
        if len(self.skills) > 0:
            skill_ratio = matched_count / len(self.skills)

        else:
            skill_ratio = 0

        # stronger skill score
        skill_score = skill_ratio * 60
        domain_score = 0
        domain_keywords = self.domain_keywords.get(
            self.domain,
            []
        )
        matched_keywords = 0

        for keyword in domain_keywords:
            if keyword in job_text:
                matched_keywords += 1

        domain_score = min(matched_keywords * 6, 25)
        role_bonus = 0
        important_roles = {
            "python_development": [
                "python developer",
                "backend developer",
                "software engineer",
                "backend engineer"
            ],
            "web_development": [
                "web developer",
                "frontend developer",
                "backend developer",
                "full stack developer"
            ],
            "machine_learning": [
                "machine learning engineer",
                "ai engineer",
                "data scientist",
                "deep learning engineer"
            ],
            "data_analyst": [
                "data analyst",
                "business analyst",
                "power bi developer",
                "analytics engineer"
            ]
        }

        for role in important_roles.get(self.domain, []):
            if role in job_text:
                role_bonus = 15
                break

        final_score = (
            (text_score * 0.20) +
            skill_score +
            domain_score +
            role_bonus
        )
        final_score = round(final_score)
        final_score = max(0, min(final_score, 100))

        return final_score, matched_skills
