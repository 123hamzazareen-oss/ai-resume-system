import base64
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from job_matcher.models import Job, MatchResult
from users.services.match_engine import MatchEngine
# ---------------------------------------------------
# HOME
# ---------------------------------------------------
def home(request):
    return render(request, 'users/home.html')

# ---------------------------------------------------
# DOMAIN BASED GMAIL SEARCH
# ---------------------------------------------------
QUERY_MAP = {
    "web_development":
        "frontend developer OR backend developer OR react OR django",
    "python_development":
        "python developer OR django OR flask OR backend engineer",
    "data_analyst":
        "data analyst OR sql OR power bi OR business analyst",
    "machine_learning":
        "machine learning OR ai engineer OR data scientist OR deep learning OR nlp"
}

# ---------------------------------------------------
# MATCH LEVEL
# ---------------------------------------------------
def get_match_level(score):
    if score >= 70:
        return "High"

    elif score >= 45:
        return "Medium"

    return "Low"

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
@login_required
def dashboard(request):
    # ---------------------------------------------------
    # CHECK RESUME
    # ---------------------------------------------------
    if 'resume_text' not in request.session:
        return redirect('/resume/upload/')

    resume_text = request.session.get(
        'resume_text',
        ''
    )
    domain = request.session.get(
        'domain',
        ''
    ).lower()
    skills = request.session.get(
        'skills',
        []
    )
    ats_score = request.session.get(
        'ats_score',
        85
    )
    missing_skills = request.session.get(
        'missing_skills',
        []
    )
    suggestions = request.session.get(
        'suggestions',
        []
    )
    jobs = []
    seen = set()
    gmail_connected = False

    # ---------------------------------------------------
    # GMAIL
    # ---------------------------------------------------
    if 'credentials' in request.session:
        gmail_connected = True
        creds = Credentials(
            **request.session['credentials']
        )
        service = build(
            'gmail',
            'v1',
            credentials=creds
        )

        # ---------------------------------------------------
        # SEARCH QUERY
        # ---------------------------------------------------
        query = QUERY_MAP.get(
            domain,
            "job OR hiring"
        )
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=30
        ).execute()
        messages = results.get(
            'messages',
            []
        )

        # ---------------------------------------------------
        # AI MATCH ENGINE
        # ---------------------------------------------------
        engine = MatchEngine(
            resume_text,
            skills,
            domain
        )

        # ---------------------------------------------------
        # PROCESS EMAILS
        # ---------------------------------------------------
        for msg in messages:
            try:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                headers = msg_data['payload'].get(
                    'headers',
                    []
                )
                subject = ""
                sender = ""

                for h in headers:
                    name = h.get(
                        'name',
                        ''
                    ).lower()

                    if name == 'subject':
                        subject = h.get(
                            'value',
                            ''
                        )

                    if name == 'from':
                        sender = h.get(
                            'value',
                            ''
                        )

                # ---------------------------------------------------
                # GMAIL SNIPPET
                # ---------------------------------------------------
                snippet = msg_data.get(
                    'snippet',
                    ''
                )

                # ---------------------------------------------------
                # EXTRACT FULL EMAIL BODY
                # ---------------------------------------------------
                body = ""
                payload = msg_data.get(
                    "payload",
                    {}
                )
                parts = payload.get(
                    "parts",
                    []
                )
                try:
                    if parts:
                        for part in parts:
                            mime_type = part.get(
                                "mimeType",
                                ""
                            )

                            if mime_type == "text/plain":
                                data = part.get(
                                    "body",
                                    {}
                                ).get(
                                    "data"
                                )

                                if data:
                                    decoded = base64.urlsafe_b64decode(
                                        data
                                    ).decode(
                                        "utf-8",
                                        errors="ignore"
                                    )
                                    body += decoded

                    else:
                        data = payload.get(
                            "body",
                            {}
                        ).get(
                            "data"
                        )

                        if data:
                            decoded = base64.urlsafe_b64decode(
                                data
                            ).decode(
                                "utf-8",
                                errors="ignore"
                            )
                            body += decoded

                except Exception as e:
                    print("BODY PARSE ERROR:", e)

                # ---------------------------------------------------
                # COMPLETE EMAIL TEXT
                # ---------------------------------------------------
                text_blob = f"""
                {subject}
                {snippet}
                {body}
                """
                text_blob_lower = text_blob.lower()

                # ---------------------------------------------------
                # SMART JOB FILTER
                # ---------------------------------------------------
                valid_keywords = [
                    "job",
                    "developer",
                    "engineer",
                    "analyst",
                    "intern",
                    "hiring",
                    "career",
                    "vacancy",
                    "machine learning",
                    "ai",
                    "deep learning",
                    "data science",
                    "nlp",
                    "computer vision",
                    "artificial intelligence",
                    "python",
                    "tensorflow",
                    "pytorch",
                    "sql",
                    "pandas"
                ]

                if not any(
                    keyword in text_blob_lower
                    for keyword in valid_keywords
                ):
                    continue

                # ---------------------------------------------------
                # EXTRACT ROLE + COMPANY
                # ---------------------------------------------------
                role = subject.strip()
                company = "Unknown"

                if " at " in subject.lower():
                    parts = subject.split(" at ")
                    role = parts[0].strip()
                    company = parts[1].strip()

                # ---------------------------------------------------
                # REMOVE DUPLICATES
                # ---------------------------------------------------
                key = f"{role}_{company}"

                if key in seen:
                    continue

                seen.add(key)

                # ---------------------------------------------------
                # AI SCORE
                # ---------------------------------------------------
                match_score, matched_skills = engine.compute_score(
                    text_blob
                )

                # ---------------------------------------------------
                # FILTER VERY LOW SCORES
                # ---------------------------------------------------
                if match_score < 15:
                    continue

                match_level = get_match_level(
                    match_score
                )

                # ---------------------------------------------------
                # SAVE JOB
                # ---------------------------------------------------
                job_obj, created = Job.objects.get_or_create(
                    title=role,
                    company=company,
                    defaults={
                        'description': snippet
                    }
                )

                # ---------------------------------------------------
                # SAVE MATCH HISTORY
                # ---------------------------------------------------
                match_obj = MatchResult.objects.filter(
                    user=request.user,
                    job=job_obj
                ).first()

                if match_obj:
                    match_obj.score = match_score
                    match_obj.match_type = match_level
                    match_obj.save()

                else:
                    MatchResult.objects.create(
                        user=request.user,
                        job=job_obj,
                        score=match_score,
                        match_type=match_level
                    )

                # ---------------------------------------------------
                # DASHBOARD JOBS
                # ---------------------------------------------------
                jobs.append({
                    "subject": role,
                    "company": company,
                    "sender": sender,
                    "match_score": match_score,
                    "match_level": match_level,
                    "matched_skills": matched_skills[:6]
                })

            except Exception as e:
                print("EMAIL ERROR:", e)
                continue

    # ---------------------------------------------------
    # MATCH HISTORY
    # ---------------------------------------------------
    previous_matches = MatchResult.objects.filter(
        user=request.user
    ).order_by('-id')[:15]

    # ---------------------------------------------------
    # SORT JOBS
    # ---------------------------------------------------
    jobs = sorted(
        jobs,
        key=lambda x: x["match_score"],
        reverse=True
    )

    # ---------------------------------------------------
    # SHOW ONLY TOP JOB MATCHES
    # ---------------------------------------------------
    jobs = jobs[:6]

    # ---------------------------------------------------
    # FINAL PAGE
    # ---------------------------------------------------
    return render(request, "users/dashboard.html", {
        "domain": domain,
        "ats_score": ats_score,
        "skills": skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "jobs": jobs,
        "gmail_connected": gmail_connected,
        "previous_matches": previous_matches
    })
