from rest_framework.views import APIView
from .serializers import (RegisterSerializer, ForgetPWDSerializers,ChangePWDSerializers,AdressAddSerializers,
                           AdressSerializers,ProfileSerializers,UserUpdateSerializers,AddBasketSerializers, GetBasketSerializers,BasketUpdateSerializers)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from accounts.models import User, Address, Basket
from rest_framework import status, permissions, generics, serializers
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.utils.encoding import force_str    
from accounts.helpers import send_activate_link, send_forgetpwd_link
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from accounts.tokens import account_activation_token
from django.utils.encoding import force_bytes
from drf_yasg import openapi




class RegisterApi(generics.CreateAPIView):
    http_method_names = ["post"]
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
    @swagger_auto_schema(
    operation_description='''yeni user yaratmag user login olanda eger gonderilen activate mailnen activate olmayibsa mail yeniden gonderilir login zad olmur
    '''
    )   
    def post(self, request, *args, **kwags):
        user_serializer = RegisterSerializer(data = self.request.data)
        data = {}
        if user_serializer.is_valid():
            user = user_serializer.save()
            data['detail'] = 'User created and send activation mail'
            data['user'] = user.get_full_name()
            data['email'] = user.email
            user.is_active = False
            user.set_password(self.request.data.get('password'))
            user.save()
            send_activate_link(user,urlsafe_base64_encode(force_bytes(user.pk)), account_activation_token.make_token(user))

        else:
            data = user_serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@swagger_auto_schema(
    operation_description='''email a gonderilen uuidb ve token daxil et hesabii aktiv et
    ''',)
def activateapi(request,uidb64, token):
    data={}
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and not user.is_active and account_activation_token.check_token(user, token)  :
        user.is_active = True   
        user.save()
        data['detail'] = 'User Activated!'
        return Response(data, status=status.HTTP_200_OK)

    else:
        data['detail'] = 'User active!'
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    



class ForgetPWD(generics.GenericAPIView):
    serializer_class = ForgetPWDSerializers
    http_method_names = ["post"]
    @swagger_auto_schema(
        operation_description='''email hasabin yaz reset linki gonderilsin
        ''',)
    def post(self, request):

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_active:
                send_forgetpwd_link(user,urlsafe_base64_encode(force_bytes(user.pk)), account_activation_token.make_token(user))
                return Response({'detail': 'We have sent a link for reset password'}, status=status.HTTP_200_OK)
            send_activate_link(user,urlsafe_base64_encode(force_bytes(user.pk)), account_activation_token.make_token(user))
            return Response({'detail': 'User not active. Activation mail sended, please first activate account'}, status=status.HTTP_202_ACCEPTED)
            
        return Response({'detail': 'User not exists'}, status=status.HTTP_404_NOT_FOUND)
        
class ChangePWD(generics.GenericAPIView):
    serializer_class = ChangePWDSerializers
    http_method_names = ["post"]
    @swagger_auto_schema(
        operation_description='''email a gonderilen uuidb ve token daxil et bide yeni password sifre deyisilsin
        ''',
        manual_parameters=[
            openapi.Parameter('uidb64', openapi.IN_QUERY, description="UIDB parameter", type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_QUERY, description="Token parameter", type=openapi.TYPE_STRING),
        ]
    )
    def post(self, request, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(self.request.GET.get('uidb64')))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, self.request.GET.get('token')) :
            user.set_password(self.request.data.get('password'))    
            user.save()
            return Response({'detail':'password changed'}, status=status.HTTP_200_OK)

        else:
            return Response({'detail':'somethings goes wrong'}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateApi(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializers
    http_method_names = ["patch"]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class ProfileApi(APIView):
    http_method_names = ["get"]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        user = User.objects.get(id = request.user.id)
        user_seri =  ProfileSerializers(user).data
        return Response(user_seri)


class AddressApi(generics.ListCreateAPIView):
    http_method_names = ["post",'get']
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdressAddSerializers
        return AdressSerializers
    @swagger_auto_schema(
        operation_description='''burada address siyahilanacag chox vaxt is defaul true olani auto select etmek olar amma bezi hallarda is default da 
        hamisi false gele biler nezere almag lazimdir.
        ''',)
    def get(self,*args,**kwargs):
        addresses = Address.objects.filter(user = self.request.user).order_by('-created_at')
        addresses_list = AdressSerializers(addresses, many = True).data
        return Response(addresses_list)
    @swagger_auto_schema(
        operation_description='''yeni address yaratmag
        ''',)
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        addresses = Address.objects.filter(user = self.request.user).order_by('-created_at')
        addresses_list = AdressSerializers(addresses, many = True).data
        return Response(addresses_list)
 
class AddressDeleteApi(generics.DestroyAPIView):
    serializer_class = AdressSerializers
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Address

    def delete(self, request, *args, **kwargs):
        address_default = self.get_object().is_default
        super().delete(request, *args, **kwargs)
        if address_default:
            last_address = Address.objects.filter(user = request.user).order_by('-created_at').first()
            if last_address:
                last_address.is_default = True
                last_address.save()
        addresses = Address.objects.filter(user = self.request.user).order_by('-created_at')
        addresses_list = AdressSerializers(addresses, many = True).data
        return Response(addresses_list)


class AddressUpdateApi(generics.UpdateAPIView):
    serializer_class = AdressSerializers
    http_method_names = ["patch"]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Address

    def update(self, request, *args, **kwargs):
        address = self.get_object()
        if request.data.get('is_default','') and address.is_default == False:
            last_default_address = Address.objects.filter(user = request.user).filter(is_default = True).first()
            if last_default_address:
                last_default_address.is_default = False
                last_default_address.save()
            address.is_default = True
            address.save()
        super().update(request, *args, **kwargs)
        addresses = Address.objects.filter(user = self.request.user).order_by('-created_at')
        addresses_list = AdressSerializers(addresses, many = True).data
        return Response(addresses_list)

    
    
class BasketApi(generics.ListCreateAPIView):
    http_method_names = ["post",'get']
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddBasketSerializers
        return GetBasketSerializers
    @swagger_auto_schema(
        operation_description='''mehsullari oxumag''',)
    def get(self,request,*args,**kwargs):
        products = Basket.objects.filter(user = request.user).order_by('-created_at')
        products_seri = GetBasketSerializers(products, many=True).data
        return Response(products_seri)
    @swagger_auto_schema(
        operation_description='''yeni mehsul elave etmek
        ''',)
    def post(self, request, *args, **kwargs):
        basket_item = Basket.objects.filter(user = request.user).filter(product_id = request.data.get('product',''))

        if basket_item:
            basket_item = basket_item.first()
            basket_item.quantity += int(request.data.get('quantity',''))
            basket_item.save()
            products = Basket.objects.filter(user = request.user).order_by('-created_at')
            products_seri = GetBasketSerializers(products, many=True).data
            return Response(products_seri)
        
        super().post(request, *args, **kwargs)
        products = Basket.objects.filter(user = request.user).order_by('-created_at')
        products_seri = GetBasketSerializers(products, many=True).data
        return Response(products_seri)
    
class BasketDeleteApi(generics.DestroyAPIView):
    serializer_class = GetBasketSerializers
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Basket
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        basketitems = Basket.objects.filter(user = self.request.user).order_by('-created_at')
        basketitems_list = GetBasketSerializers(basketitems, many = True).data
        return Response(basketitems_list)
    
class BasketUpdateApi(generics.UpdateAPIView):
    serializer_class = BasketUpdateSerializers
    http_method_names = ["patch"]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Basket
    @swagger_auto_schema(
        operation_description='''basketde olan mehsulun basket id sine esasesn sayi  deyishir
        ''',)
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        basketitems = Basket.objects.filter(user = self.request.user).order_by('-created_at')
        basketitems_list = GetBasketSerializers(basketitems, many = True).data
        return Response(basketitems_list)