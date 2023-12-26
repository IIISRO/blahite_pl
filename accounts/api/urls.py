from django.urls import path, re_path
from .views import (RegisterApi, activateapi, ForgetPWD, ChangePWD, AddressApi, AddressDeleteApi,
                    AddressUpdateApi,UserUpdateApi, ProfileApi, BasketApi, BasketDeleteApi, BasketUpdateApi)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


app_name = 'accountsApi'


urlpatterns = [
    path('auth/register/', RegisterApi.as_view(), name = 'register'),
    re_path(r'^auth/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
    activateapi, name='activate'),
    path('auth/forgetpwd/', ForgetPWD.as_view(), name = 'forgetpwd'),
    path('auth/changepwd/', ChangePWD.as_view(), name='changepwd'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', ProfileApi.as_view(), name='profile'),
    path('auth/user/update/<int:pk>/', UserUpdateApi.as_view(), name='user_update'),
    path('auth/address/', AddressApi.as_view(), name='address'),
    path('auth/address/delete/<int:pk>/', AddressDeleteApi.as_view(), name='address_delete'),
    path('auth/address/update/<int:pk>/', AddressUpdateApi.as_view(), name='address_update'),
    path('auth/basket/', BasketApi.as_view(), name='basket'),
    path('auth/basket/delete/<int:pk>/', BasketDeleteApi.as_view(), name='basket_delete'),
    path('auth/basket/update/<int:pk>/', BasketUpdateApi.as_view(), name='basket_update'),






    


]