# ✦ AI Resume Analyzer & Smart Job Matcher

An intelligent, Django-powered web platform designed to analyze professional resumes, calculate compatibility scores, and automate career discovery by scanning email inboxes.

---

## 🚀 Key Features

*   **Intelligent Resume Parsing:** Automatically extracts text, identifies professional skills, and detects domains from PDF and Word (`.docx`) documents.
*   **Real-Time Score Engine:** Computes compatibility scores out of 100 based on standard industry taxonomies.
*   **Gmail Integration (OAuth 2.0):** Securely scans your Gmail inbox (read-only) for career-related emails.
*   **AI-Powered Similarity Matching:** Utilizes **TF-IDF Vectorization** and **Cosine Similarity** to compare resume content with fetched email bodies and list matching jobs.
*   **Interactive Dashboard:** Displays resume insights, missing skills, suggestions, and a live history of job matches with compatibility ratings (High, Medium, Low).

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python / Django | Robust, secure web frame for application logic. |
| **Database** | PostgreSQL | Scalable relational database for user data and match history. |
| **Parsing** | PyMuPDF (fitz) / Python-Docx | High-performance document processors for PDF and DOCX. |
| **AI / NLP** | Scikit-Learn | TF-IDF & Cosine Similarity vector matching engine. |
| **API / Auth** | Google OAuth2 / Gmail API | Official Google API client for inbox scanning. |
| **Configuration** | Python-Dotenv | Safe management of credentials via `.env` file. |

---

## 📈 System Architecture & Flow

```text
       [ User Uploads Resume ]
                 │
                 ▼
     [ Text & Skill Extraction ]
                 │
                 ▼
    [ Detect Career Track/Domain ]
                 │
                 ▼
   [ Connect Gmail via Google OAuth ]
                 │
                 ▼
   [ Scan Inbox for Career Emails ]
                 │
                 ▼
  [ Compute Cosine Similarity Matching ]
                 │
                 ▼
 [ View Matched Jobs on User Dashboard ]
```

---

## 📦 Project Directory Structure

```bash
ai_resume_system/
├── ai_resume_system/      # Django settings and routing config
├── users/                 # Authentication backend and dashboard views
├── resume_analyzer/       # PDF/Word text parsing and skill extractor
├── job_matcher/           # Database models for jobs and match results
├── gmail_integration/     # OAuth 2.0 Gmail scanning logic
├── templates/             # HTML templates and UI layout
├── static/                # CSS styles, images, and static assets
├── .env                   # Local configuration variables (ignored in Git)
├── credentials.json       # Google Console OAuth credentials
├── manage.py              # Django execution manager
└── requirements.txt       # Python package dependencies
```

---

## ⚙️ Installation & Setup

Follow these steps to run the application locally on your machine.

### Prerequisites
*   Python 3.8+
*   PostgreSQL
*   Google Cloud Console access (for Gmail API integration)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/ai-resume-system.git
cd ai-resume-system
```

---

### Step 2: Set Up Virtual Environment

#### Windows
```powershell
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables (`.env`)
Create a `.env` file in the root directory and add the following settings:

```env
# Django Configurations
SECRET_KEY=your-django-secret-key
DEBUG=True

# PostgreSQL Database Settings
DB_NAME=Resume_Analyzer
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

---

### Step 5: Initialize the PostgreSQL Database
Create a PostgreSQL database matching the name in your `.env` file:
```sql
CREATE DATABASE Resume_Analyzer;
```

---

### Step 6: Google OAuth & Gmail API Setup
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project and enable the **Gmail API**.
3.  Set up the OAuth consent screen and create **OAuth 2.0 Client IDs** credentials (Web Application type).
4.  Add `http://127.0.0.1:8000/gmail/callback/` to your Authorized Redirect URIs.
5.  Download the client configuration JSON file and rename it to **`credentials.json`**.
6.  Place **`credentials.json`** directly inside the root folder of the project.

---

### Step 7: Run Migrations & Start Server
Apply database migrations to configure PostgreSQL tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

Create an admin account:
```bash
python manage.py createsuperuser
```

Launch the development server:
```bash
python manage.py runserver
```
Visit the application at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔒 Security & Privacy Notes

*   **Google OAuth 2.0 Consent:** The Gmail connection requests **read-only** inbox scopes. The application does not have permission to send, edit, or delete messages.
*   **Secure Environment Settings:** Database passwords and Django secret keys are protected outside the source code using the local `.env` configuration file.