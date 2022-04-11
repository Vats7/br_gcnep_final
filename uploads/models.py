from django.db import models
from home.models import BaseModel


class FileUpload(BaseModel):
    file = models.FileField(upload_to='file_uploads')
    notes = models.CharField(max_length=200)
    processed = models.BooleanField(default=False)

