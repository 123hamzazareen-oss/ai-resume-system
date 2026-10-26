import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ResumeUploadForm
from .models import Resume
from .utils import (
    extract_text,
    extract_skills,
    detect_domain,
    calculate_ats_score,
    get_missing_skills,
    generate_suggestions,
    SKILL_CATEGORIES
)

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            resume = None
            try:
                resume = form.save(commit=False)
                resume.user = request.user
                resume.save()
                file_path = resume.file.path
                text = extract_text(file_path)

                if not text or len(text.strip()) < 20:
                    if resume.file and os.path.exists(resume.file.path):
                        try:
                            os.remove(resume.file.path)
                        except OSError:
                            pass
                    resume.delete()
                    return render(request, 'resume_analyzer/upload.html', {
                        'form': form,
                        'error': 'Unable to extract text from the uploaded resume. Please upload a clear PDF or Word (.docx) document.'
                    })

                skills = extract_skills(text)
                domain = detect_domain(skills)
                ats_score = calculate_ats_score(skills, domain)
                missing_skills = get_missing_skills(skills, domain)
                suggestions = generate_suggestions(
                    skills,
                    missing_skills,
                    domain,
                    ats_score
                )
                resume.extracted_text = text
                resume.skills = ", ".join(skills)
                resume.ats_score = ats_score
                resume.save()

                request.session['resume_text'] = text
                request.session['skills'] = skills
                request.session['domain'] = domain
                request.session['ats_score'] = ats_score
                request.session['missing_skills'] = missing_skills
                request.session['suggestions'] = suggestions
                request.session['resume_id'] = resume.id

                messages.success(request, f"Resume '{resume.filename}' parsed and analyzed successfully!")
                return redirect('resume_result')

            except Exception as e:
                print("ERROR:", e)
                if resume and resume.pk:
                    if resume.file and os.path.exists(resume.file.path):
                        try:
                            os.remove(resume.file.path)
                        except OSError:
                            pass
                    resume.delete()

                return render(request, 'resume_analyzer/upload.html', {
                    'form': form,
                    'error': f"Processing error: {str(e)}"
                })
        else:
            return render(request, 'resume_analyzer/upload.html', {
                'form': form,
                'error': "Invalid file format or corrupt file. Please select a valid PDF or Word (.docx) document."
            })

    else:
        form = ResumeUploadForm()

    latest_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()

    return render(request, 'resume_analyzer/upload.html', {
        'form': form,
        'latest_resume': latest_resume
    })

@login_required
def resume_result(request, resume_id=None):
    resume = None
    if resume_id:
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    elif 'resume_id' in request.session:
        resume = Resume.objects.filter(id=request.session['resume_id'], user=request.user).first()

    if not resume:
        resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()

    if not resume and 'resume_text' not in request.session:
        messages.info(request, "Please upload a resume first to view the AI analysis report.")
        return redirect('upload_resume')

    if resume:
        skills = [s.strip() for s in resume.skills.split(",") if s.strip()]
        domain = detect_domain(skills)
        ats_score = resume.ats_score if resume.ats_score else calculate_ats_score(skills, domain)
        missing_skills = get_missing_skills(skills, domain)
        suggestions = generate_suggestions(skills, missing_skills, domain, ats_score)

        request.session['resume_text'] = resume.extracted_text
        request.session['skills'] = skills
        request.session['domain'] = domain
        request.session['ats_score'] = ats_score
        request.session['missing_skills'] = missing_skills
        request.session['suggestions'] = suggestions
        request.session['resume_id'] = resume.id
    else:
        skills = request.session.get('skills', [])
        domain = request.session.get('domain', 'general')
        ats_score = request.session.get('ats_score', 0)
        missing_skills = request.session.get('missing_skills', [])
        suggestions = request.session.get('suggestions', [])

    domain_display = domain.replace('_', ' ').title() if domain else 'General Track'
    domain_expected_skills = SKILL_CATEGORIES.get(domain, [])
    matched_domain_skills = list(set(skills) & set(domain_expected_skills))
    other_skills = list(set(skills) - set(matched_domain_skills))

    if ats_score >= 75:
        score_tier = "High"
        score_verdict = "Excellent Alignment for Enterprise Roles"
        score_color = "#10b981"
    elif ats_score >= 45:
        score_tier = "Medium"
        score_verdict = "Moderate Match - Recommended Enhancements Available"
        score_color = "#f59e0b"
    else:
        score_tier = "Low"
        score_verdict = "Needs Key Skill & Domain Alignment"
        score_color = "#f43f5e"

    word_count = len(resume.extracted_text.split()) if resume and resume.extracted_text else 0

    return render(request, 'resume_analyzer/result.html', {
        'resume': resume,
        'domain': domain,
        'domain_display': domain_display,
        'ats_score': int(ats_score),
        'score_tier': score_tier,
        'score_verdict': score_verdict,
        'score_color': score_color,
        'skills': skills,
        'matched_domain_skills': matched_domain_skills,
        'other_skills': other_skills,
        'domain_expected_skills': domain_expected_skills,
        'missing_skills': missing_skills,
        'suggestions': suggestions,
        'word_count': word_count,
    })

