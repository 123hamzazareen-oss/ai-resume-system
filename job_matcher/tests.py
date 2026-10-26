from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from job_matcher.models import Job, MatchResult
from job_matcher.views import simple_skill_match, classify_match as classify_view
from job_matcher.utils import calculate_similarity, classify_match as classify_utils
from resume_analyzer.models import Resume

class JobMatcherUtilsTests(TestCase):
    def test_simple_skill_match_valid(self):
        score, matched = simple_skill_match("python, django, sql", "We are hiring a Python and Django developer")
        self.assertEqual(score, 66.7)
        self.assertEqual(set(matched), {"python", "django"})

    def test_simple_skill_match_empty_skills(self):
        score, matched = simple_skill_match("", "Some job text")
        self.assertEqual(score, 0)
        self.assertEqual(matched, [])

    def test_simple_skill_match_substring_false_positive(self):
        """Testing if simple_skill_match falsely matches single letters or subwords inside unrelated words"""
        score, matched = simple_skill_match("c, go, r", "Looking for a react developer with django experience")
        self.assertNotIn("c", matched, "False positive: 'c' matched 'react'")
        self.assertNotIn("go", matched, "False positive: 'go' matched 'django'")
        self.assertNotIn("r", matched, "False positive: 'r' matched 'developer'")

    def test_calculate_similarity_empty_inputs(self):
        try:
            score = calculate_similarity("", "job text", "python")
            self.assertIsInstance(score, (int, float))
        except Exception as e:
            self.fail(f"calculate_similarity crashed on empty resume_text: {e}")

    def test_classify_match_consistency(self):
        """Checks if classify_match in utils and views are consistent with each other"""
        score = 70
        tier_view = classify_view(score)    # Expected: "High" (>= 65)
        tier_utils = classify_utils(score)  # Returns: "Medium Match" (< 75)
        # Note the architectural mismatch: one returns 'High', another returns 'Medium Match'!
        self.assertIn("High", tier_utils, f"Score of 70 returned contradictory tiers: view='{tier_view}' vs utils='{tier_utils}'")


class JobMatcherViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='jobseeker', password='Password123!')
        self.job1 = Job.objects.create(
            title='Senior Python Engineer',
            company='TechCorp',
            description='Looking for Python, Django, and SQL expertise'
        )
        self.job2 = Job.objects.create(
            title='Frontend Designer',
            company='DesignCo',
            description='Looking for HTML, CSS, Figma'
        )

    def test_match_jobs_requires_login(self):
        response = self.client.get(reverse('job_matches'))
        self.assertEqual(response.status_code, 302)

    def test_match_jobs_with_resume(self):
        self.client.login(username='jobseeker', password='Password123!')
        Resume.objects.create(
            user=self.user,
            file='resumes/test.pdf',
            skills='python, django',
            extracted_text='Python Django Developer'
        )
        response = self.client.get(reverse('job_matches'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        self.assertEqual(response.context['total_count'], 2)
        # Job 1 should be ranked higher than Job 2
        results = response.context['results']
        self.assertEqual(results[0]['job'].title, 'Senior Python Engineer')
