from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from resume_analyzer.models import Resume
from .models import Job

def simple_skill_match(resume_skills, job_description):
    skills = [s.strip().lower() for s in resume_skills.split(",") if s.strip()]
    job_text = job_description.lower()

    if not skills:
        return 0, []

    matched = []
    for skill in skills:
        if skill in job_text:
            matched.append(skill)

    score = (len(matched) / len(skills)) * 100
    return round(score, 1), matched

def classify_match(score):
    if score >= 65:
        return "High"
    elif score >= 35:
        return "Medium"
    else:
        return "Low"

@login_required
def match_jobs(request):
    try:
        resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()

        if not resume:
            return render(request, 'job_matcher/matches.html', {
                'error': "No resume found. Please upload a resume first to evaluate job matches."
            })

        query = request.GET.get('q', '').strip().lower()
        filter_tier = request.GET.get('tier', '').strip().lower()

        jobs = Job.objects.all().order_by('-id')
        results = []

        for job in jobs:
            score, matched_skills = simple_skill_match(resume.skills, job.description)
            match_type = classify_match(score)

            if filter_tier and match_type.lower() != filter_tier:
                continue

            if query and (query not in job.title.lower() and query not in job.company.lower() and query not in job.description.lower()):
                continue

            results.append({
                'job': job,
                'score': score,
                'match_type': match_type,
                'matched_skills': matched_skills
            })

        # Sort by score descending
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        high_count = sum(1 for r in results if r['match_type'] == 'High')
        medium_count = sum(1 for r in results if r['match_type'] == 'Medium')
        low_count = sum(1 for r in results if r['match_type'] == 'Low')

        return render(request, 'job_matcher/matches.html', {
            'resume': resume,
            'results': results,
            'query': query,
            'filter_tier': filter_tier,
            'high_count': high_count,
            'medium_count': medium_count,
            'low_count': low_count,
            'total_count': len(results)
        })

    except Exception as e:
        return render(request, 'job_matcher/matches.html', {
            'error': str(e)
        })

