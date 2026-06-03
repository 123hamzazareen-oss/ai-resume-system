import os
import base64
import re
from email import message_from_bytes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_flow():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:8000/gmail/callback/'
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
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
        else:
            data = payload.get('body', {}).get('data')

        if data:
            text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            emails.append(text)

    return emails

def extract_job_from_email(text):
    text = text.lower()
    job = {}

    if "developer" in text:
        job['title'] = "Developer"
    elif "engineer" in text:
        job['title'] = "Engineer"
    else:
        job['title'] = "Job Opportunity"

    company_match = re.search(r'at ([a-zA-Z ]+)', text)
    if company_match:
        job['company'] = company_match.group(1)
    else:
        job['company'] = "Unknown"

    job['description'] = text[:1000]

    return job
