import os
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import JobEmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@login_required
def connect_gmail(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['state'] = state
    request.session['code_verifier'] = flow.code_verifier

    return redirect(authorization_url)

@login_required
def gmail_callback(request):
    if 'error' in request.GET:
        messages.warning(request, f"Google authorization was not completed: {request.GET.get('error')}")
        return redirect('/dashboard/')

    state = request.session.get('state')
    code_verifier = request.session.get('code_verifier')
    try:
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_OAUTH_CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        flow.code_verifier = code_verifier
        flow.fetch_token(
            authorization_response=request.build_absolute_uri()
        )
        credentials = flow.credentials
        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        messages.success(request, "Gmail inbox connected successfully!")
    except Exception as e:
        messages.error(request, f"Failed to connect Gmail: {str(e)}")

    return redirect('/dashboard/')

@login_required
def gmail_status(request):
    if 'credentials' in request.session:
        return HttpResponse("Connected")
    return HttpResponse("Not Connected")

@login_required
def test_gmail(request):
    if 'credentials' not in request.session:
        return HttpResponse("Not connected")

    try:
        creds = Credentials(**request.session['credentials'])
        service = build('gmail', 'v1', credentials=creds)
        service.users().messages().list(userId='me', maxResults=1).execute()
        return HttpResponse("Gmail API WORKING ")
    except Exception as e:
        return HttpResponse(f"Gmail API Error: {str(e)}", status=500)

@login_required
def gmail_inbox(request):
    if 'credentials' not in request.session:
        return redirect('/gmail/connect/')

    try:
        creds = Credentials(**request.session['credentials'])
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(
            userId='me',
            q="job OR hiring OR developer OR engineer",
            maxResults=10
        ).execute()
        messages_items = results.get('messages', [])
    except Exception as e:
        return render(request, 'gmail_integration/inbox.html', {
            'emails': [],
            'error': f"Failed to fetch Gmail messages: {str(e)}"
        })

    email_list = []
    resume_text = request.session.get('resume_text', '')
    if not resume_text:
        resume_text = "python django react javascript html css"

    for msg in messages_items:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        payload = msg_data.get('payload', {})
        headers = payload.get('headers', [])
        subject = None
        sender = 'Unknown'

        for h in headers:
            name = h.get('name', '').lower()
            if name == 'subject':
                subject = h.get('value')
            elif name == 'from':
                sender = h.get('value', 'Unknown')

        if not subject or subject.strip() == "":
            subject = msg_data.get('snippet', 'No Subject')

        company = "Unknown"
        role = subject or "Job Opportunity"

        if subject and " at " in subject:
            parts = subject.split(" at ")
            role = parts[0]
            company = parts[1]

        keywords = ['job', 'developer', 'engineer', 'hiring', 'interview']
        is_job = any(k in (subject or '').lower() for k in keywords)

        job = JobEmail.objects.filter(user=request.user, subject=subject).first()
        if job:
            job.sender = sender
            job.role = role
            job.company = company
            job.is_job = is_job
            job.save()
        else:
            job = JobEmail.objects.create(
                user=request.user,
                subject=subject,
                sender=sender,
                role=role,
                company=company,
                is_job=is_job
            )

        email_list.append({
            'subject': subject,
            'role': job.role,
            'company': job.company,
            'sender': job.sender,
            'is_job': job.is_job,
        })

    return render(request, 'gmail_integration/inbox.html', {'emails': email_list})
