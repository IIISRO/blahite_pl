from rest_framework import serializers
from core.models import SliderImages


class SliderImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = SliderImages
        fields = (
            'path',
        )
    

