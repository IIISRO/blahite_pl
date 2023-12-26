from django.urls import path
from .views import SliderImagesApi


app_name = 'coreApi'

urlpatterns = [
    path('sliderimages/', SliderImagesApi.as_view(), name = 'sliderApi'),

]