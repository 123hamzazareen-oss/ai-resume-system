import os
from django import forms
from django.core.exceptions import ValidationError
from .models import Resume

ALLOWED_EXTENSIONS = ['.pdf', '.docx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError("Please select a file to upload.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(f"Unsupported file format '{ext}'. Only PDF and Word (.docx) documents are permitted.")

        if file.size > MAX_FILE_SIZE:
            raise ValidationError("File size exceeds 10MB limit. Please upload a smaller document.")

        return file
