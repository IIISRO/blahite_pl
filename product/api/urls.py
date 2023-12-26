from django.urls import path
from .views import CategoriesApi, ProductApi, CategoryListApi, ProductSearchApi 


app_name = 'productApi'

urlpatterns = [
    path('categories/', CategoriesApi.as_view(), name = 'categoriesApi'),
    path('products/<path:category_slug>/', CategoryListApi.as_view(), name = 'productListApi'),
    path('products/', ProductSearchApi.as_view(), name = 'productListApi'),
    path('product/<path:category_slug>/<slug:product_slug>/', ProductApi.as_view(), name = 'productApi'),



]