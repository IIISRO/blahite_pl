from product.models import Category
from rest_framework.views import APIView
from .serializers import CategorySerializer, ProductSerializer, ProductSearchSerializer, CategoryProductListSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import  permissions
from product.models import Category, Variants
from django.db.models import Q, Subquery
from django.core.paginator import EmptyPage, Paginator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi





class CategoriesApi(APIView):
    http_method_names = ["get"]
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(
        operation_description='''Burada sehifedeki categoryler teqdim olunur. Eger axtardiginiz category alt categorydise siz bunu parentlerin tamamlayaraq tapa bilesiniz.
        dinlediyiniz uchun teshekkurler.
        '''
    )
    def get(self, request, *args, **kwags):
        categories = Category.objects.filter(parent = None)
        categories_list = CategorySerializer(categories, many = True).data
        return Response(categories_list)

class ProductApi(APIView):
    http_method_names = ["get"]
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(
        operation_description='''Bu API vasitesi ile muvafiq axtaris neticesinde sehifedeki mehsulun detail sehifesine kece bilersiz. Burada acilan variantin hansi
        producta bagli oldugu ve onun basqa hansi variantlarinin oldugu gosterirlir. axtarisi ise mehsulun categorylerini yeni mehsul alt categorydise meselen sport shoes
        buzaman onun bagli oldugu butun ust categorilerin slug qeyd edilmelidir sonda ise mehsulun slug. <i>footwear/shoes/sportshoes/<b>mehsulin adi</b>/</i>.
        Asagidaki categor sluga <i>footwear/shoes/sportshoes/</i> product sluga ise mehsulun adini daxil edin vse.
        '''
    )
    def get(self,*args,**kwargs):
        category_slug = self.kwargs.get('category_slug')
        product_slug = self.kwargs.get('product_slug')
        variants = get_object_or_404(Variants, slug = product_slug)
        if not variants.get_absolute_url() == f'/{category_slug}/{product_slug}':
            raise Http404   
        variant = ProductSerializer(variants).data
        return Response(variant)
    
class CategoryListApi(APIView):
    http_method_names = ["get"]
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(
        operation_description='''Bu API categoriya sehifesine gore productlarin listidir. Asagidaki <b>page</b>, <b>order</b>, <b>price</b> keyleri staticdir bulara gore mueyyen filterler olur.
        Eger mehsulun propertylerine gore filer vermek isteyirsinizse, gonderilen filter datasinin key ve value lerinden istifade ede bilersiz.<i>(color=red,blue&size=m)</i>.
        <b>price</b> querysine <u>"200;500"</u> kimi, <b>order</b> <u>"-actual_price"</u> veya <u>"actual_price"</u>, <b>page</b> ise gonderilen muvafiq integerleri.
        ''',
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page parameter", type=openapi.TYPE_INTEGER),
            openapi.Parameter('order', openapi.IN_QUERY, description="Order parameter", type=openapi.TYPE_STRING),
            openapi.Parameter('price', openapi.IN_QUERY, description="Price parameter", type=openapi.TYPE_STRING),
        ]
    )
    def get(self,*args,**kwargs):
        
        category_slug = self.kwargs.get('category_slug')
        category = Category.objects.filter(slug = category_slug.split('/')[-1]).first()
        if not category or not category.get_absolute_url() == f'/{category_slug}':
            raise Http404
        

        category_childs = category.get_childs()
        
        if not category_childs:
            variants = Variants.objects.filter(product__category = category)
        else:
            variants = Variants.objects.filter(product__category = category)
            for child_cat in category_childs:
                variants = variants.union(Variants.objects.filter(product__category = child_cat))
           
        if variants:
            property_dict = {}
            for j in variants:
                variant_values = j.variantoption.all()
                for k in variant_values:
                    for i in k.property_value.all():
                        property = i.property.property
                        value = i.values
                        if property_dict.get(property) is None:
                            property_dict[property]=[value]
                        elif value not in property_dict.get(property):
                            property_dict[property].append(value)

            if len(self.request.GET)==1 and 'page' in self.request.GET:
                pass
            else:
                filters = dict(self.request.GET)
                for k,v in filters.items():
                        if k == 'price':
                            variants = Variants.objects.filter(id__in=Subquery(variants.values('id'))).filter(actual_price__range = (v[0].split(";")[0],v[0].split(";")[1]))
                        elif k == 'order':   
                            variants = Variants.objects.filter(id__in=Subquery(variants.values('id'))).order_by(v[0])
                        elif k!='page':
                            variants = Variants.objects.filter(id__in=Subquery(variants.values('id'))).filter(variantoption__property_value__values__in = v[0].split(',')).distinct()
            if variants:
        
                product_per_page=6

                page = self.request.GET.get('page', 1)
                product_paginator = Paginator(variants, product_per_page)
                try:
                    variants = product_paginator.page(page)
                except EmptyPage:
                    variants = product_paginator.page(product_paginator.num_pages)
                except:
                    variants = product_paginator.page(product_per_page)

                if product_paginator.num_pages > 1:
                    is_paginated = True
                else:
                    is_paginated=False

                pagination = {}
                pagination['is_paginated']=is_paginated
                pagination['all_pages_num'] = product_paginator.num_pages
                pagination['current_page'] = int(page)
                pagination['next_page'] = None if not variants.has_next() else variants.next_page_number()  
                pagination['previous']  = None if not variants.has_previous() else variants.previous_page_number()  
                variants_json = CategoryProductListSerializer(variants, many = True).data
                
                response_json = {}
                response_json['pagination'] = pagination
                response_json['filters'] = property_dict
                response_json['products'] = variants_json
            else:
                pagination = {}
                pagination['is_paginated']=False
                pagination['all_pages_num'] = 0
                pagination['current_page'] = 0
                pagination['next_page'] = 0 
                pagination['previous']  = 0  
                
                response_json = {}
                response_json['pagination'] = pagination
                response_json['filters'] = property_dict
                response_json['products'] = []

            return Response(response_json)
        



        raise Http404

class ProductSearchApi(APIView):
    http_method_names = ["get"]
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(
        operation_description='''Bu API butun mehsullarin listidir. Asagidaki  <b>search</b>, <b>category</b>, <b>page</b>, <b>order</b>, <b>price</b> keyleri staticdir bulara gore mueyyen filterler olur.
        Eger mehsulun propertylerine gore filer vermek isteyirsinizse, gonderilen filter datasinin key ve value lerinden istifade ede bilersiz.<i>(color=red,blue&size=m)</i>. Hemcinin category de 
        eyni qaydada gonderilern categorylernen. <b>search</b> query si ile mehsul title na gore axtaris ede bilersiz.
        <b>price</b> querysine <u>"200;500"</u> kimi, <b>order</b> <u>"-actual_price"</u> veya <u>"actual_price"</u>, <b>page</b> ise gonderilen muvafiq integerleri.
        ''',
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Size parameter", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page parameter", type=openapi.TYPE_INTEGER),
            openapi.Parameter('order', openapi.IN_QUERY, description="Order parameter", type=openapi.TYPE_STRING),
            openapi.Parameter('price', openapi.IN_QUERY, description="Price parameter", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Category parameter", type=openapi.TYPE_STRING),
        ]
    )
    def get(self,*args,**kwargs):
        products = Variants.objects.all()
        property_dict = {}

        for j in products:
                variant_values = j.variantoption.all()
                for k in variant_values:
                    for i in k.property_value.all():
                        property = i.property.property
                        value = i.values
                        if property_dict.get(property) is None:
                            property_dict[property]=[value]
                        elif value not in property_dict.get(property):
                            property_dict[property].append(value)
        category_list = []
        
        for product in products:
            variant_category = product.product.category.title
        
            if variant_category not in category_list:
                category_list.append(variant_category)


        if len(self.request.GET)==1 and 'page' in self.request.GET:
            pass
  
        else:
            filters = dict(self.request.GET)
            for k,v in filters.items():
                    
                    if k=='search':
                        products = Variants.objects.filter(Q(title__icontains=v[0])|Q(title__startswith = v[0])|Q(title__endswith = v[0]))

                        category_list.clear()
                        for product in products:
                            variant_category = product.product.category.title
                        
                            if variant_category not in category_list:
                                category_list.append(variant_category)
                                
                        property_dict.clear()
                        for j in products:
                            variant_values = j.variantoption.all()
                            for k in variant_values:
                                for i in k.property_value.all():
                                    property = i.property.property
                                    value = i.values
                                    if property_dict.get(property) is None:
                                        property_dict[property]=[value]
                                    elif value not in property_dict.get(property):
                                        property_dict[property].append(value)
                    elif k == 'order':   
                        products = products.order_by(v[0])
                    elif k == 'price':
                        products = products.filter(actual_price__range = (v[0].split(";")[0],v[0].split(";")[1]))
                    elif k == 'category':
                        products = products.filter(product__category__title = v[0])
                    elif k!='page':
                        products = products.filter(variantoption__property_value__values__in = v[0].split(',')).distinct()
                    
                    
        if products:
    
            product_per_page=6

            page = self.request.GET.get('page', 1)
            product_paginator = Paginator(products, product_per_page)
            try:
                products = product_paginator.page(page)
            except EmptyPage:
                products = product_paginator.page(product_paginator.num_pages)
            except:
                products = product_paginator.page(product_per_page)

            if product_paginator.num_pages > 1:
                is_paginated = True
            else:
                is_paginated=False

            pagination = {}
            pagination['is_paginated']=is_paginated
            pagination['all_pages_num'] = product_paginator.num_pages
            pagination['current_page'] = int(page)
            pagination['next_page'] = None if not products.has_next() else products.next_page_number()  
            pagination['previous']  = None if not products.has_previous() else products.previous_page_number()  
            
            variants_json = ProductSearchSerializer(products, many = True).data



            response_json = {}
            response_json['pagination'] = pagination
            response_json['filters'] = property_dict
            response_json['categories'] = category_list
            response_json['products'] = variants_json
        else:
            pagination = {}
            pagination['is_paginated']=False
            pagination['all_pages_num'] = 0
            pagination['current_page'] = 0
            pagination['next_page'] = 0 
            pagination['previous']  = 0  
            
            response_json = {}
            response_json['pagination'] = pagination
            response_json['filters'] = property_dict
            response_json['categories'] = category_list
            response_json['products'] = []





     
    

        
        return Response(response_json)



     
    