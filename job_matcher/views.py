import re
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from resume_analyzer.models import Resume
from .models import Job

def simple_skill_match(resume_skills, job_description):
    if not resume_skills or not job_description:
        return 0, []

    skills = [s.strip().lower() for s in resume_skills.split(",") if s.strip()]
    job_text = job_description.lower()

    if not skills:
        return 0, []

    matched = []
    for skill in skills:
        escaped = re.escape(skill)
        if re.search(r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])', job_text):
            matched.append(skill)

    score = (len(matched) / len(skills)) * 100
    return round(score, 1), matched

def classify_match(score):
    if score >= 70:
        return "High"
    elif score >= 45:
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
        all_evaluated = []

        for job in jobs:
            score, matched_skills = simple_skill_match(resume.skills, job.description)
            match_type = classify_match(score)

            if query and (query not in job.title.lower() and query not in job.company.lower() and query not in job.description.lower()):
                continue

            all_evaluated.append({
                'job': job,
                'score': score,
                'match_type': match_type,
                'matched_skills': matched_skills
            })

        # Calculate accurate counts across all matching jobs before tier filtering
        high_count = sum(1 for r in all_evaluated if r['match_type'] == 'High')
        medium_count = sum(1 for r in all_evaluated if r['match_type'] == 'Medium')
        low_count = sum(1 for r in all_evaluated if r['match_type'] == 'Low')
        total_count = len(all_evaluated)

        # Now apply tier filter to results displayed
        if filter_tier:
            results = [r for r in all_evaluated if r['match_type'].lower() == filter_tier]
        else:
            results = all_evaluated

        # Sort by score descending
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        return render(request, 'job_matcher/matches.html', {
            'resume': resume,
            'results': results,
            'query': query,
            'filter_tier': filter_tier,
            'high_count': high_count,
            'medium_count': medium_count,
            'low_count': low_count,
            'total_count': total_count
        })

    except Exception as e:
        return render(request, 'job_matcher/matches.html', {
            'error': str(e)
        })

