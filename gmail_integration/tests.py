import os
import inspect
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from gmail_integration.models import JobEmail
from gmail_integration.utils import extract_job_from_email, get_flow

class GmailIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='gmailuser', password='Password123!')

    def test_extract_job_from_email_patterns(self):
        sample_email = "We are seeking a Python Developer at Acme Corp to build microservices."
        job = extract_job_from_email(sample_email)
        self.assertEqual(job['title'], "Developer")
        self.assertEqual(job['company'].strip().lower(), "acme corp")

    def test_get_flow_uses_settings_file_path(self):
        """Testing that get_flow() uses settings.GOOGLE_OAUTH_CLIENT_SECRETS_FILE instead of hardcoded string"""
        import gmail_integration.utils as gmail_utils
        source = inspect.getsource(gmail_utils.get_flow)
        self.assertIn("GOOGLE_OAUTH_CLIENT_SECRETS_FILE", source)

    @patch('gmail_integration.views.build')
    def test_gmail_inbox_duplicate_subject_does_not_crash(self, mock_build):
        """Verify that multiple emails with identical subjects do not raise MultipleObjectsReturned"""
        self.client.login(username='gmailuser', password='Password123!')
        session = self.client.session
        session['credentials'] = {
            'token': 'fake_token',
            'refresh_token': 'fake_refresh',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'fake_id',
            'client_secret': 'fake_secret',
            'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
        }
        session.save()

        # Mock gmail service response with duplicate subject emails
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()
        mock_messages.list().execute.return_value = {
            'messages': [{'id': 'msg1'}, {'id': 'msg2'}]
        }
        mock_messages.get().execute.side_effect = [
            {
                'id': 'msg1',
                'snippet': 'Job alert 1',
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': 'Weekly Job Alert'},
                        {'name': 'From', 'value': 'jobs1@test.com'}
                    ]
                }
            },
            {
                'id': 'msg2',
                'snippet': 'Job alert 2',
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': 'Weekly Job Alert'},
                        {'name': 'From', 'value': 'jobs2@test.com'}
                    ]
                }
            }
        ]
        mock_build.return_value = mock_service

        response = self.client.get(reverse('gmail_inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 2)
