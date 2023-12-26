from django.db import models
from django.utils.safestring import mark_safe

# Create your models here.

class AbstractModel(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class SliderImages(AbstractModel):
    path = models.ImageField(upload_to="SliderImages")
    def __str__(self):
        return f'{self.id}'
    def image_tag(self):
        return mark_safe(f'<img src="{self.path.url}" alt="no img" height="50"/>')

    class Meta:
        verbose_name_plural = "SliderImages"
    