from core.models import SliderImages
from rest_framework.views import APIView
from .serializers import SliderImagesSerializer
from rest_framework.response import Response
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema


class SliderImagesApi(APIView):
    http_method_names = ["get"]
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(
    operation_description='''burdada hecne cagirirsan  shekiller gelir vse.
    '''
    )   
    def get(self, request, *args, **kwags):
        images = SliderImages.objects.all()
        images_list = SliderImagesSerializer(images, many = True).data
        return Response(images_list)

