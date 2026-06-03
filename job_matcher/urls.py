from django.urls import path
from .views import match_jobs
urlpatterns = [
    path('', match_jobs, name='job_matches'),
]
