from django.db import models


class file_data(models.Model):
    # title = models.CharField(max_length=100)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # def __str__(self):
    #     print('self',self.file.file.name)
    #     return self.file.file.name
   