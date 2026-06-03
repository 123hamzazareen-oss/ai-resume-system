from django.urls import path
from . import views
urlpatterns = [
    path('connect/', views.connect_gmail, name='connect_gmail'),
    path('callback/', views.gmail_callback, name='gmail_callback'),
    path('status/', views.gmail_status, name='gmail_status'),
    path('test/', views.test_gmail, name='test_gmail'),
    path('inbox/', views.gmail_inbox, name='gmail_inbox'),
]
