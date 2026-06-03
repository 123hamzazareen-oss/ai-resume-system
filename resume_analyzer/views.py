from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ResumeUploadForm
from .models import Resume
from .utils import (
    extract_text,
    extract_skills,
    detect_domain,
    calculate_ats_score,
    get_missing_skills,
    generate_suggestions
)

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                resume = form.save(commit=False)
                resume.user = request.user
                resume.save()
                file_path = resume.file.path
                text = extract_text(file_path)

                if not text or len(text.strip()) < 20:
                    return render(request, 'resume_analyzer/upload.html', {
                        'form': form,
                        'error': 'Unable to extract text from resume.'
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

                return redirect('/dashboard/')

            except Exception as e:
                print("ERROR:", e)

                return render(request, 'resume_analyzer/upload.html', {
                    'form': form,
                    'error': str(e)
                })

    else:
        form = ResumeUploadForm()

    return render(request, 'resume_analyzer/upload.html', {
        'form': form
    })
