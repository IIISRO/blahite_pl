from rest_framework import serializers, status
from accounts.models import User, Address, Basket
from product.models import Images
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.helpers import send_activate_link
from django.utils.http import  urlsafe_base64_encode
from accounts.tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import APIException
from django.utils.encoding import force_str

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required = True)
    number = serializers.CharField(required = True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)

    class Meta:
        model = User
        fields = [
            'email',
            'number',
            'first_name',
            'last_name',
            'password',
        ]
        extra_kwargs = {
            'password':{'write_only':True}
        }

        def save(self):
            user = User(
                email = self.validated_data['email'],
                number = self.validated_data['number'],
                first_name = self.validated_data['first_name'],
                last_name = self.validated_data['last_name'],
            )

                
            user.save()
            return user
        
class UserUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [  
            'number',
            'first_name',
            'last_name',
            ]
        

class ForgetPWDSerializers(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class ChangePWDSerializers(serializers.Serializer):
    password = serializers.CharField(write_only=True)


    class Meta:
        fields = ['password']

class AdressSerializers(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id',
            'user',
            'address',
            'address2',
            'postal',
            'province',
            'cities',
            'is_default'
        )
class ProfileSerializers(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [  
            'id',   
            'email',
            'number',
            'first_name',
            'last_name',
            'addresses'
            ]
    def get_addresses(self,obj):
        addresses=Address.objects.filter(user=obj)
        addresses_seri = AdressAddSerializers(addresses, many=True).data
        return addresses_seri

class AdressAddSerializers(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only = True)
    class Meta:
        model = Address
        fields = (
            'user',
            'address',
            'address2',
            'postal',
            'province',
            'cities'
        )

    def validate(self, attrs):
        request = self.context['request']
        attrs['user'] = request.user
        if Address.objects.filter(user = request.user).filter(is_default = True).exists():
            last_default_address = Address.objects.filter(user = request.user).filter(is_default = True).first()
            last_default_address.is_default=False
            last_default_address.save()
        return super().validate(attrs)
      



class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, status_code):
        if status_code is not None:self.status_code = status_code
        if detail is not None:
            self.detail =  force_str(detail)
        else: self.detail = {'detail': force_str(self.default_detail)}

class JWTLoginSerializers(TokenObtainPairSerializer):
      def validate(self, attrs):    
        if User.objects.filter(email = attrs.get('email')).exists():
            user = User.objects.get(email = attrs.get('email'))
            if check_password(attrs.get('password'),user.password):
                if not user.is_active:
                    send_activate_link(user,urlsafe_base64_encode(force_bytes(user.pk)), account_activation_token.make_token(user))
                    raise CustomValidation('user not active activation mail sended',status_code=status.HTTP_202_ACCEPTED)
        # data['id'] = self.user.id
        # data['email'] = self.user.email
        # data['number'] = self.user.number
        # data['first_name'] = self.user.first_name
        # data['last_name'] = self.user.last_name

        return super().validate(attrs)

class AddBasketSerializers(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only = True)
    class Meta:
        model = Basket
        fields = (
            'user',
            'product',
            'quantity',
        )
    def validate(self, attrs):
        request = self.context['request']
        attrs['user'] = request.user
        return super().validate(attrs)
    
class GetBasketSerializers(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    img = serializers.SerializerMethodField()


    class Meta:
        model = Basket
        fields = (
            'id',
            'product',
            'quantity',
            'img'
            
        )
    def get_product(self, obj):
        product = {}
        product['product_id'] = obj.product.variant.id
        product['product'] = obj.product.variant.product.title
        product['title'] = obj.product.variant.title
        product['price'] = obj.product.variant.price
        product['discount'] = obj.product.variant.discount_type
        product['discount_amount'] = obj.product.variant.discount_amount
        product['actual_price'] = obj.product.variant.actual_price
        product['stock'] = obj.product.variant.stock
        product['quantity'] = obj.product.quantity

        properties = {}
        for i in obj.product.property_value.all():
            properties[i.property.property] = i.values
            
        product['properties'] = properties
        product['url'] = obj.product.variant.get_absolute_url()

        
        return product
    def get_img(self, obj):
        image = Images.objects.filter(variant = obj.product.variant).filter(is_main = True).first()
        if image:
            return image.image.url
        return  ''
    
class BasketUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = [  
            'quantity',
            ]
        