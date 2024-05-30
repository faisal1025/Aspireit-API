from django.db import models
from django.contrib.auth.models import User

def upload_to(instance, filename):
    return f'images/{filename}'

class FileModel(models.Model):
    creator = models.ForeignKey(User, 
                                on_delete=models.CASCADE, related_name='files', default=1)
    file = models.FileField(upload_to=upload_to, blank=True, null=True)
    description = models.TextField()

