# AI Resume Analyzer and Smart Job Matching System with Gmail Integration

AI Resume Analyzer and Smart Job Matching System is a Django-based intelligent web application that helps users analyze resumes, calculate ATS scores, and discover suitable job opportunities automatically using AI and NLP techniques.

The system also integrates with Gmail using OAuth 2.0 to fetch job-related emails and compare them with the uploaded resume for smart job matching.

---

# Features

- User Registration and Authentication
- Resume Upload (PDF and DOCX)
- Resume Text Extraction
- Skill Detection
- Domain Detection
- ATS Score Calculation
- Missing Skills Identification
- Resume Improvement Suggestions
- AI-Based Job Matching
- Gmail Job Email Fetching
- Smart Match Classification
- Interactive Dashboard
- Match History Tracking

---

# Technologies Used

## Backend
- Python
- Django

## Frontend
- HTML
- CSS
- Bootstrap 5

## Database
- PostgreSQL

## AI / NLP
- Scikit-learn
- TF-IDF Vectorizer
- Cosine Similarity

## APIs
- Gmail API
- Google OAuth 2.0

## Libraries
- PyMuPDF (fitz)
- python-docx
- google-api-python-client
- google-auth-oauthlib

---

# Project Workflow

```text
User Uploads Resume
        ↓
Resume Text Extraction
        ↓
Skill Extraction
        ↓
Domain Detection
        ↓
ATS Score Calculation
        ↓
Resume Suggestions
        ↓
Gmail Job Fetching
        ↓
AI Job Matching
        ↓
Dashboard Results
```

---

# System Modules

## 1. Resume Analyzer Module

This module handles:
- Resume upload
- PDF/DOCX parsing
- Text extraction
- Skill extraction
- ATS score generation
- Missing skills detection
- Suggestions generation

Supported formats:
- PDF
- DOCX

---

## 2. Job Matching Module

This module compares:
- Resume skills
- Resume text
- Job descriptions

The matching engine uses:
- TF-IDF
- Cosine Similarity
- Skill matching
- Domain-based scoring
- Role bonus scoring

Jobs are classified into:
- High Match
- Medium Match
- Low Match

---

## 3. Gmail Integration Module

This module:
- Connects Gmail using OAuth 2.0
- Fetches job-related emails
- Extracts:
  - Job title
  - Company name
  - Sender information
- Filters hiring emails
- Matches jobs with user resume

---

## 4. Dashboard Module

The dashboard displays:
- ATS score
- Skills
- Missing skills
- Suggestions
- Live job matches
- Match percentage
- Previous match history

---

# AI Matching Logic

The project uses hybrid matching logic.

## TF-IDF Similarity
TF-IDF is used to compare resume text with job descriptions.

## Cosine Similarity
Cosine Similarity calculates similarity scores between:
- Resume content
- Job requirement text

## Skill Matching
The system checks how many resume skills exist in the job description.

## Domain Boost
Extra score is added when the job belongs to the detected user domain.

## Role Bonus
Additional score is added for important roles like:
- Python Developer
- Data Analyst
- Machine Learning Engineer
- Backend Developer

---

# ATS Score Calculation

ATS score is calculated based on:
- Skills found in the resume
- Matching domain skills
- Resume keyword optimization

The final score is generated out of 100.

---

# Supported Domains

- Web Development
- Python Development
- Machine Learning
- Data Analyst

---

# Project Structure

```bash
ai_resume_system/
│
├── users/
├── resume_analyzer/
├── job_matcher/
├── gmail_integration/
├── templates/
├── static/
├── media/
├── manage.py
└── requirements.txt
```

---

# Installation Guide

## 1. Clone Repository

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

# Required Packages

```bash
pip install django
pip install psycopg2
pip install pymupdf
pip install python-docx
pip install scikit-learn
pip install google-api-python-client
pip install google-auth-oauthlib
```

---

# PostgreSQL Setup

Create database:

```sql
CREATE DATABASE Resume_Analyzer;
```

Update database settings inside:

```python
ai_resume_system/settings.py
```

Example:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Resume_Analyzer',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

# Gmail API Setup

## Step 1
Open Google Cloud Console

## Step 2
Create a new project

## Step 3
Enable Gmail API

## Step 4
Create OAuth Credentials

## Step 5
Download:

```text
credentials.json
```

Place the file in the project root directory.

---

# Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# Create Superuser

```bash
python manage.py createsuperuser
```

---

# Run the Project

```bash
python manage.py runserver
```

Open browser:

```text
http://127.0.0.1:8000/
```

---

# Example Features

## Resume Analysis
- Resume ATS Score
- Skill Detection
- Missing Skills
- Resume Suggestions

## Job Matching
- Match Percentage
- High/Medium/Low Match
- Skill Comparison

## Gmail Integration
- Job Email Fetching
- Hiring Email Detection
- Smart Job Matching

---

# Security Features

- Django Authentication System
- Gmail OAuth 2.0 Authentication


---

# Future Improvements
- AI Career Chatbot
- Resume PDF Reports
- Advanced NLP Models
- Interview Preparation System
- Admin Analytics Dashboard

---

# Contributors

- Hamza Zareen
- Muhammad Uzair

---

# License

This project is developed for educational and Final Year Project purposes.

---

# Conclusion

AI Resume Analyzer and Smart Job Matching System with Gmail Integration is an intelligent web platform that helps students and job seekers improve resumes, calculate ATS compatibility, and discover suitable job opportunities automatically using NLP and AI-based matching techniques.