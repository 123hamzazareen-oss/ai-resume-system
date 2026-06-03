from django.contrib import admin
from django.urls import path, include
from users import views as user_views   
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('', include('users.urls')),
    path('resume/', include('resume_analyzer.urls')),
    path('jobs/', include('job_matcher.urls')),
    path('gmail/', include('gmail_integration.urls')),
]
