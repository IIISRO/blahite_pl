from django.db import models
from core.models import AbstractModel
from product.models import Options
from django.contrib.auth.models import AbstractUser
# Create your models here.

    
class User(AbstractUser):
    username = None
    email = models.EmailField(('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    number = models.CharField(max_length=20,null=True,blank=True)

class Address(AbstractModel):
    user = models.ForeignKey('User',on_delete=models.CASCADE)
    region = models.CharField(max_length=50,default='Polska')
    address = models.CharField(max_length=250, null=False, blank=False)
    address2 = models.CharField(max_length=250, null=True, blank=True)
    postal = models.CharField(max_length= 10, null=False, blank=False)
    province = models.CharField(max_length= 100, null=False, blank=False)
    cities = models.CharField(max_length=100, null=False, blank=False) 
    is_default = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Address'

class Basket(AbstractModel):
    user = models.ForeignKey('User',on_delete=models.CASCADE)
    product = models.ForeignKey(Options,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) :
        return f'{self.product}({self.user.email})'