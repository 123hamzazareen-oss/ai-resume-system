import os
import base64
import re
from email import message_from_bytes
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_flow():
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    return flow

def get_gmail_service(credentials_dict):
    creds = Credentials(**credentials_dict)
    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_emails(service):
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = msg_data.get('payload', {})
        parts = payload.get('parts', [])
        data = ""

        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        break
        else:
            data = payload.get('body', {}).get('data')

        if data:
            text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            emails.append(text)

    return emails

def extract_job_from_email(text):
    if not text:
        return {'title': 'Job Opportunity', 'company': 'Unknown', 'description': ''}
    text_lower = text.lower()
    job = {}

    if "developer" in text_lower:
        job['title'] = "Developer"
    elif "engineer" in text_lower:
        job['title'] = "Engineer"
    elif "analyst" in text_lower:
        job['title'] = "Analyst"
    else:
        job['title'] = "Job Opportunity"

    # Non-greedy company regex stopping before prepositions or sentence continuation
    company_match = re.search(r'\bat\s+([a-zA-Z0-9&.\'\-]+(?:\s+[a-zA-Z0-9&.\'\-]+){0,3})(?=\s+(?:to|for|with|in|is|are|seeking|looking|\n|\.|\,|$))', text, re.IGNORECASE)
    if not company_match:
        company_match = re.search(r'\bat\s+([a-zA-Z0-9&.\'\-]+(?:\s+[a-zA-Z0-9&.\'\-]+){0,2})', text, re.IGNORECASE)

    if company_match:
        job['company'] = company_match.group(1).strip()
    else:
        job['company'] = "Unknown"

    job['description'] = text[:1000]

    return job
