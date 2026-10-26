import os
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from users.forms import RegisterForm, LoginForm
from users.backends import EmailOrUsernameModelBackend
from users.services.match_engine import MatchEngine
from resume_analyzer.models import Resume
from job_matcher.models import Job, MatchResult

class UserRegistrationTests(TestCase):
    def test_successful_registration(self):
        form_data = {
            'first_name': 'Hamza',
            'last_name': 'Zareen',
            'email': 'hamza@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, 'hamza@example.com')
        self.assertEqual(user.username, 'hamza')
        self.assertTrue(user.check_password('Password123!'))

    def test_duplicate_email_case_insensitive(self):
        User.objects.create_user(username='hamza1', email='hamza@example.com', password='Password123!')
        form_data = {
            'first_name': 'Hamza',
            'last_name': 'Khan',
            'email': 'HAMZA@EXAMPLE.COM',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        form_data = {
            'first_name': 'Hamza',
            'last_name': 'Khan',
            'email': 'hamza2@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)

    def test_weak_passwords(self):
        cases = [
            'short1!',         # < 8 chars
            'nocapsornum!',     # no caps, no num
            'NOLOWERORNUM!',    # no lower, no num
            'NoNumberHere!',    # no number
            'NoSpecialChar123', # no special char
        ]
        for pwd in cases:
            form = RegisterForm(data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': f'test_{pwd[:4]}@example.com',
                'password': pwd,
                'confirm_password': pwd
            })
            self.assertFalse(form.is_valid(), f"Password '{pwd}' should fail validation")

    def test_username_collision_generation(self):
        User.objects.create_user(username='alex', email='alex1@domain.com', password='Password123!')
        form = RegisterForm(data={
            'first_name': 'Alex',
            'last_name': 'Two',
            'email': 'alex@otherdomain.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'alex1')


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='JohnDoe@Example.com',
            password='SecretPassword123!'
        )
        self.backend = EmailOrUsernameModelBackend()

    def test_login_with_username(self):
        user = self.backend.authenticate(None, username='johndoe', password='SecretPassword123!')
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_login_with_username_case_insensitive(self):
        user = self.backend.authenticate(None, username='JohnDoe', password='SecretPassword123!')
        self.assertIsNotNone(user)

    def test_login_with_email_case_insensitive(self):
        user = self.backend.authenticate(None, username='johndoe@example.com', password='SecretPassword123!')
        self.assertIsNotNone(user)

    def test_login_with_invalid_password(self):
        user = self.backend.authenticate(None, username='johndoe', password='WrongPassword')
        self.assertIsNone(user)

    def test_login_with_nonexistent_user(self):
        user = self.backend.authenticate(None, username='nonexistent', password='SecretPassword123!')
        self.assertIsNone(user)

    def test_empty_credentials(self):
        self.assertIsNone(self.backend.authenticate(None, username='', password=''))
        self.assertIsNone(self.backend.authenticate(None, username=None, password=None))


class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )

    def test_login_and_logout(self):
        Resume.objects.create(
            user=self.user,
            file='resumes/sample.pdf',
            extracted_text='Python Django developer with PostgreSQL skills',
            skills='python, django',
            ats_score=80.0
        )
        response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        logout_resp = self.client.get(reverse('logout'))
        self.assertEqual(logout_resp.status_code, 302)

    def test_open_redirect_vulnerability_on_login(self):
        """Testing whether login validates ?next= against unvalidated external URLs"""
        malicious_urls = [
            'https://evil.com',
            '//evil.com',
            'http://attacker.com/steal-creds'
        ]
        for url in malicious_urls:
            response = self.client.post(f"{reverse('login')}?next={url}", {
                'username_or_email': 'testuser',
                'password': 'TestPassword123!'
            })
            # A secure app must NOT redirect directly to the external malicious domain!
            self.assertFalse(
                response.url.startswith('http://') or response.url.startswith('https://') or response.url.startswith('//'),
                f"Security Vulnerability: Open Redirect to {response.url}"
            )

    def test_dashboard_without_resume_redirects(self):
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/resume/upload/', response.url)

    def test_dashboard_with_resume(self):
        self.client.login(username='testuser', password='TestPassword123!')
        Resume.objects.create(
            user=self.user,
            file='resumes/sample.pdf',
            extracted_text='Python Django developer with PostgreSQL skills',
            skills='python, django',
            ats_score=80.0
        )
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')


class MatchEngineTests(TestCase):
    def test_match_engine_with_none_and_edge_inputs(self):
        # Should not raise AttributeError when inputs are None or empty
        try:
            engine = MatchEngine(resume_text=None, skills=[], domain="python_development")
            score, matched = engine.compute_score("Python backend developer required")
            self.assertIsInstance(score, int)
            self.assertIsInstance(matched, list)
        except Exception as e:
            self.fail(f"MatchEngine failed on None resume_text: {e}")

    def test_match_engine_with_none_job_text(self):
        engine = MatchEngine("Python Django", ["python", "django"], "python_development")
        try:
            score, matched = engine.compute_score(None)
        except Exception as e:
            self.fail(f"MatchEngine crashed on None job_text: {e}")

    def test_substring_false_positive_skill_matching(self):
        """Testing if skills without word boundaries falsely match substrings in job descriptions"""
        engine = MatchEngine("React Developer", ["c", "go", "r"], "web_development")
        # In the job text, the words are 'react' (contains 'c'), 'django' (contains 'go'), 'developer' (contains 'r')
        # None of C, Go, or R programming languages are requested here!
        job_text = "Looking for a react frontend engineer with django knowledge"
        score, matched = engine.compute_score(job_text)
        self.assertNotIn("c", matched, "False positive: 'c' matched 'react'")
        self.assertNotIn("go", matched, "False positive: 'go' matched 'django'")
        self.assertNotIn("r", matched, "False positive: 'r' matched 'developer'")
