from django.db import models

# Create your models here.

from core.models import AbstractModel
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify
from core.models import AbstractModel



class Product(AbstractModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
        ('New','New')

    )
    title = models.CharField(max_length=150)
    brand = models.CharField(max_length=150)
    category = models.ForeignKey('Category', on_delete=models.CASCADE) #many to one relation with Category
    status=models.CharField(max_length=50,default='New', choices=STATUS)
    description = models.TextField(max_length=255)
    detail = RichTextUploadingField()
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.title

    
    # def save(self,*args, **kwargs):
    #     exs = Product.objects.filter(slug=self.slug)
    #     if len(exs)>=1:
    #         self.slug = f'{slugify(self.title)}-{self.id}'

    #     super(Product, self).save(*args, **kwargs)


    # method to create a fake table field in read only mode
    def image_tag(self):
        if Variants.objects.filter(product = self).exists():
            variant = Variants.objects.filter(product = self)
            if Images.objects.filter(variant = variant.first()).exists():
                image = Images.objects.filter(variant = variant.first())
                return mark_safe('<img src="{}" height="50"/>'.format(image.first().image.url))
            else:
                return mark_safe('<img src="" alt="no img" height="50"/>')

        else:
            return mark_safe('<img src="" alt="no img" height="50"/>')

    def get_absolute_url(self):
        return f'{self.category.get_absolute_url()}/{self.slug}'


    # order sayin tapmaga metodlar


class Variants(AbstractModel):

    DISCOUNT_TYPE = (
        ('PRECENT' ,'Precent'),
        ('AMOUNT' , 'Amount')
    )
    title = models.CharField(max_length=100, blank=False,null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock=models.BooleanField(default=True)
    price=models.FloatField(default=0.00)
    discount_type=models.CharField(max_length=50, null=True, blank=True, choices=DISCOUNT_TYPE)
    discount_amount=models.FloatField(null=True, blank=True)
    actual_price=models.FloatField(null=True, blank=True)
    slug = models.SlugField(null=False, unique=True)


    class Meta:
        verbose_name_plural = "Variants"

    def __str__(self):
        return self.title

            
    def save(self,*args, **kwargs):
        # exs = Variants.objects.filter(slug=self.slug)
        # if len(exs)>=1:
        #     self.slug = f'{slugify(self.title)}-{self.id}'
        if self.discount_amount:
            if self.discount_type == 'PRECENT':
                self.actual_price=round(self.price-((self.price*self.discount_amount)/100),2)
                # wishlists = accounts.models.WishList.objects.filter(product=self)
                # if wishlists:
                #     for wish in wishlists:
                #         email = wish.user.email
                #         product = wish.product
                #         send_sale_mail(email, product)
                    
            elif self.discount_type == 'AMOUNT':
                self.actual_price=round(self.price-self.discount_amount,2)
                # wishlists = accounts.models.WishList.objects.filter(product=self)
                # if wishlists:
                #     for wish in wishlists:
                #         email = wish.user.email
                #         product = wish.product
                #         send_sale_mail(email, product)
        else: 
            self.actual_price=round(self.price,2)
        super(Variants, self).save(*args, **kwargs)
 

    def image_tag(self):
        if Images.objects.filter(variant=self).filter(is_main=True).exists():
            img = Images.objects.filter(variant=self).filter(is_main=True)
            return mark_safe('<img src="{}" height="50"/>'.format(img.first().image.url))
        else:
            return mark_safe('<img src="" alt="no img" height="50"/>')

    def get_absolute_url(self):
        return f'{self.product.category.get_absolute_url()}/{self.slug}'

class Options(AbstractModel):
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE, related_name='variantoption')
    property_value = models.ManyToManyField('PropertyValue')
    quantity = models.IntegerField(default=1)
    stock=models.BooleanField(default=True)

    def __str__(self):
        return f'{self.variant.title}(option)'

    def image_tag(self):
        if Variants.objects.filter(id = self.variant.id).exists():
            variant = Variants.objects.filter(id = self.variant.id)
            if Images.objects.filter(variant = variant.first()).exists():
                image = Images.objects.filter(variant = variant.first())
                return mark_safe('<img src="{}" height="50"/>'.format(image.first().image.url))
            else:
                return mark_safe('<img src="" alt="no img" height="50"/>')

        else:
            return mark_safe('<img src="" alt="no img" height="50"/>')
    class Meta:
        verbose_name_plural = "Options"

class Property(AbstractModel):
    property=models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Properties"
    def __str__(self):
        return self.property
    def save(self,*args, **kwargs):

        self.property = self.property.lower()
        super(Property, self).save(*args, **kwargs)

class PropertyValue(AbstractModel):
    values=models.CharField(max_length=50)
    property=models.ForeignKey('Property', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.property}==>{self.values}'
    def save(self,*args, **kwargs):

        self.values = self.values.lower()
        super(PropertyValue, self).save(*args, **kwargs)
    

class Images(AbstractModel):
    variant=models.ForeignKey('Variants',on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to='ProductImages/')
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Images"

    def __str__(self):
        return f'{self.variant.title}|IMG'
    







class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
        ('New', 'New')
    )
    parent = TreeForeignKey('self',blank=True, null=True ,related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    status = models.CharField(max_length=10, default='New', choices=STATUS)
    detail = RichTextUploadingField(blank=True, null=True)
    slug = models.SlugField(null=False, unique=True)
    image=models.ImageField(blank=True,upload_to='CategoriesImages/')
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

    class MPTTMeta:
        order_insertion_by = ['title']

    def get_absolute_url(self):
        if self.parent:
            categories = []
            categories.append(self.slug)
            categories.append(self.parent.slug)
            if self.parent.parent:
                most_parent = self.parent.parent
                categories.append(most_parent.slug)
                while True:
                    if most_parent.parent:
                        most_parent = most_parent.parent
                        categories.append(most_parent.slug)
                    else:
                        break
            return f"/{'/'.join(categories[::-1])}"
        else:
            return f'/{self.slug}'  
        
    def save(self,*args, **kwargs):

        self.title = self.title.lower()
        super(Category, self).save(*args, **kwargs)

   

    
    def get_childs(self):
        children = self.children.all()
        
        child_categories = []
        for child in children:
            child_categories.append(child)
            child_categories.extend(child.get_childs())
        
        return child_categories

        
    # def __str__(self):                           # __str__ method elaborated later in
    #     full_path = [self.title]                  # post.  use __unicode__ in place of
    #     k = self.parent
    #     while k is not None:
    #         full_path.append(k.title)
    #         k = k.parent
    #     return ' / '.join(full_path[::-1])

