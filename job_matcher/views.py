from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from resume_analyzer.models import Resume
from .models import Job

def simple_skill_match(resume_skills, job_description):
    resume_skills = [s.strip().lower() for s in resume_skills.split(",") if s.strip()]
    job_text = job_description.lower()

    if not resume_skills:
        return 0

    matched = 0

    for skill in resume_skills:
        if skill in job_text:
            matched += 1

    score = (matched / len(resume_skills)) * 100
    return round(score, 2)

def classify_match(score):
    if score >= 70:
        return "High Match"
    elif score >= 40:
        return "Medium Match"
    else:
        return "Low Match"

@login_required
def match_jobs(request):
    try:
        resume = Resume.objects.filter(user=request.user).last()

        if not resume:
            return render(request, 'job_matcher/matches.html', {
                'error': "Upload resume first."
            })

        jobs = Job.objects.all()
        results = []

        for job in jobs:
            score = simple_skill_match(resume.skills, job.description)
            match_type = classify_match(score)
            results.append({
                'job': job,
                'score': score,
                'match_type': match_type
            })

        return render(request, 'job_matcher/matches.html', {
            'results': results
        })

    except Exception as e:
        return render(request, 'job_matcher/matches.html', {
            'error': str(e)
        })
