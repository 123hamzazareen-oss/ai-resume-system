import os
import io
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from resume_analyzer.models import Resume
from resume_analyzer.utils import (
    extract_skills,
    detect_domain,
    calculate_ats_score,
    get_missing_skills,
    generate_suggestions,
    extract_text
)

class ResumeUtilsTests(TestCase):
    def test_extract_skills_exact_match(self):
        text = "I am skilled in Python, Django, and SQL."
        skills = extract_skills(text)
        self.assertIn("python", skills)
        self.assertIn("django", skills)
        self.assertIn("sql", skills)

    def test_extract_skills_substring_false_positives(self):
        """
        Critical Bug: Substring matching without word boundaries causes common English
        words like 'process', 'success', 'rapid', 'capital' to falsely trigger skills
        like 'css' and 'api'.
        """
        # Text with NO mention of CSS or API
        text = "I improved the agile process and achieved great success with rapid delivery."
        skills = extract_skills(text)
        self.assertNotIn("css", skills, "False Positive: 'css' was matched inside 'process' or 'success'!")
        self.assertNotIn("api", skills, "False Positive: 'api' was matched inside 'rapid'!")

    def test_detect_domain(self):
        self.assertEqual(detect_domain(["python", "django", "flask"]), "python_development")
        self.assertEqual(detect_domain(["html", "css", "javascript"]), "web_development")
        self.assertEqual(detect_domain(["tensorflow", "pytorch", "deep learning"]), "machine_learning")
        self.assertEqual(detect_domain(["pandas", "power bi", "excel"]), "data_analyst")
        self.assertEqual(detect_domain([]), "general")
        self.assertEqual(detect_domain(["carpentry", "gardening"]), "general")

    def test_calculate_ats_score_unknown_domain_does_not_crash(self):
        """Passing an unexpected or None domain shouldn't crash with KeyError"""
        try:
            score = calculate_ats_score(["python"], "unknown_track")
            self.assertIsInstance(score, int)
        except KeyError:
            self.fail("calculate_ats_score crashed with KeyError on unknown domain")

    def test_get_missing_skills_unknown_domain_does_not_crash(self):
        try:
            missing = get_missing_skills(["python"], "unknown_track")
            self.assertIsInstance(missing, list)
        except KeyError:
            self.fail("get_missing_skills crashed with KeyError on unknown domain")


class ResumeUploadSecurityAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')

    def test_upload_disallows_dangerous_file_extensions(self):
        """Uploading non-PDF / non-DOCX files (like .exe, .sh, .py, .html) should be rejected"""
        self.client.login(username='user1', password='Password123!')
        dangerous_file = SimpleUploadedFile(
            "malicious.py",
            b"import os; os.system('echo hacked')",
            content_type="text/x-python"
        )
        response = self.client.post(reverse('upload_resume'), {'file': dangerous_file})
        
        # Verify no Resume object was created in database
        self.assertEqual(Resume.objects.count(), 0, "A dangerous .py file was saved to the database!")

    def test_upload_corrupt_file_does_not_leave_zombie_database_record(self):
        """If text extraction fails on a corrupt or empty PDF, the partial Resume record must not persist in DB"""
        self.client.login(username='user1', password='Password123!')
        corrupt_file = SimpleUploadedFile(
            "corrupt.pdf",
            b"not a valid pdf content",
            content_type="application/pdf"
        )
        response = self.client.post(reverse('upload_resume'), {'file': corrupt_file})
        
        # The view should return an error message to the user, and NOT leave an empty record in DB
        self.assertEqual(Resume.objects.filter(extracted_text='').count(), 0, "Corrupt upload left an empty Resume in DB!")

    def test_idor_protection_on_resume_detail(self):
        """User 2 should NOT be able to view User 1's resume"""
        resume1 = Resume.objects.create(
            user=self.user1,
            file='resumes/user1.pdf',
            extracted_text='User 1 Private Resume Data',
            skills='python, django',
            ats_score=90.0
        )
        self.client.login(username='user2', password='Password123!')
        response = self.client.get(reverse('resume_result_detail', kwargs={'resume_id': resume1.id}))
        self.assertEqual(response.status_code, 404, "Security Bug: User 2 can view User 1's resume (IDOR)!")
