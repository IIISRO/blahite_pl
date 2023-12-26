from django.contrib import admin
from .models import SliderImages
import admin_thumbnails

# Register your models here.

class SliderImagesAdmin(admin.ModelAdmin):
    list_display = ['image_tag','path']
    readonly_fields = ('image_tag',)


admin.site.register(SliderImages,SliderImagesAdmin)
