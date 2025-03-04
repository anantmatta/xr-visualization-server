from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(f'Unsupported file extension. Allowed extensions are: {", ".join(settings.ALLOWED_UPLOAD_EXTENSIONS)}')

def validate_file_size(value):
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f'File too large. Size should not exceed {settings.MAX_UPLOAD_SIZE/1024/1024:.1f} MB.')

class UploadedFile(models.Model):
    UPLOAD_STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('uploaded', 'Upload Complete'),
        ('upload_failed', 'Upload Failed'),
    ]
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending Processing'),
        ('processing', 'Processing'),
        ('completed', 'Processing Complete'),
        ('failed', 'Processing Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        validators=[validate_file_extension, validate_file_size]
    )
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload_status = models.CharField(max_length=20, choices=UPLOAD_STATUS_CHOICES, default='uploading')
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='pending')
    processed_file = models.FileField(upload_to='processed/%Y/%m/%d/', null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    processing_parameters = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.original_filename} - {self.user.username}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the files when the model instance is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        if self.processed_file:
            if os.path.isfile(self.processed_file.path):
                os.remove(self.processed_file.path)
        super().delete(*args, **kwargs)
