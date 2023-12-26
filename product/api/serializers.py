from rest_framework import serializers
from product.models import Category, Variants, Images, Options

class VariantOptionSerializers(serializers.ModelSerializer):
    property_value = serializers.SerializerMethodField()
    class Meta:
        model = Options
        fields = (
            'id',
            'stock',
            'quantity',
            'property_value',
        )
    def get_property_value(self, obj):
        options = obj.property_value.all()
        option_dict = {}
        for option in options:
            property = option.property.property
            value = option.values
            option_dict[property]=value
        return option_dict 

class ProductVariantsSerializers(serializers.ModelSerializer):

    variant_properties = serializers.SerializerMethodField()
    all_variant_properties =  serializers.SerializerMethodField()
    variant_options = serializers.SerializerMethodField()
    all_variant_options = serializers.SerializerMethodField()
    main_img = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()


    class Meta:
        model = Variants
        fields = (
        'title',
        'main_img',
        'variant_properties',
        'all_variant_properties',
        'variant_options',
        'all_variant_options',
        'stock',
        'price',
        'discount_type',
        'discount_amount',
        'actual_price',
        'url' 
    )

    def get_variant_product(self, obj):
        variant_product = {}
        variant_product['title'] = obj.product.title
        variant_product['brand'] = obj.product.brand
        variant_product['category'] = obj.product.category.title
        variant_product['status'] = obj.product.status
        variant_product['description'] = obj.product.description
        variant_product['detail'] = obj.product.detail



        return variant_product
    def get_variant_properties(self, obj):
        options =  obj.variantoption.all()
        property_dict = {}
        for option in options:
            option_values = option.property_value.all()
            for i in option_values:
                property = i.property.property
                value = i.values
                if property_dict.get(property) is None:
                    property_dict[property]=[value]
                else:
                    if value not in property_dict[property]:
                        property_dict[property].append(value)
        return property_dict
    def get_all_variant_properties(self,obj):
        variants =  Variants.objects.filter(product = obj.product)
        property_dict = {}
        for variant in variants:
            options =  variant.variantoption.all()
            for option in options:
                option_values = option.property_value.all()
                for i in option_values:
                    property = i.property.property
                    value = i.values
                    if property_dict.get(property) is None:
                        property_dict[property]=[value]
                    else:
                        if value not in property_dict[property]:
                            property_dict[property].append(value)
        return property_dict 
    def get_variant_options(self,obj):

        return VariantOptionSerializers(obj.variantoption.all(), many=True).data
    
    def get_all_variant_options(self, obj):
        variants =  Variants.objects.filter(product = obj.product)
        options = []
        for variant in variants:
            options.append(VariantOptionSerializers(variant.variantoption.all(), many=True).data)
        return options

    # def get_variant_property(self, obj):
    #     variant_values = obj.property_value.all()
    #     property_dict = {}
    #     for i in variant_values:
    #         property = i.property.property
    #         value = i.values
    #         if property_dict.get(property) is None:
    #             property_dict[property]=[value]
    #         elif value not in property_dict.get(property):
    #             property_dict[property].append(value)
    #     return property_dict


    
    def get_main_img(self, obj):
        if Images.objects.filter(variant = obj).filter(is_main = True).exists():
            main_img = Images.objects.filter(variant = obj).filter(is_main = True).first() 
            return main_img.image.url
        return ''




    def get_url(self, obj):
    
        return obj.get_absolute_url()
    



class CategorySerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    # categories_properties = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()


    class Meta:
        model = Category
        fields = (
            'title',
            'image',
            'status',
            'detail',
            # 'categories_properties',
            'url',
            'children'
        )
    


    def get_children(self, obj):   
        if Category.objects.filter(parent = obj): 
            children = CategorySerializer(Category.objects.filter(parent = obj), many=True).data
            return children
        else: return None

    def get_url(self,  obj):
        return obj.get_absolute_url()


    

class ProductSerializer(serializers.ModelSerializer):

    variant_product = serializers.SerializerMethodField()
    variant_properties = serializers.SerializerMethodField()
    all_variant_properties = serializers.SerializerMethodField()
    variant_options = serializers.SerializerMethodField()
    all_variant_options = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    main_img = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Variants
        fields = (
            'title',
            'variant_product',
            'main_img',
            'images',
            'variant_properties',
            'all_variant_properties',
            'variant_options',
            'all_variant_options',
            'variants',
            'stock',
            'price',
            'discount_type',
            'discount_amount',
            'actual_price',
            'url' 
        )

    def get_variant_product(self, obj):
        variant_product = {}
        variant_product['title'] = obj.product.title
        variant_product['brand'] = obj.product.brand
        variant_product['category'] = obj.product.category.title
        variant_product['status'] = obj.product.status
        variant_product['description'] = obj.product.description
        variant_product['detail'] = obj.product.detail

        return variant_product

    def get_variant_properties(self, obj):
        options =  obj.variantoption.all()
        property_dict = {}
        for option in options:
            option_values = option.property_value.all()
            for i in option_values:
                property = i.property.property
                value = i.values
                if property_dict.get(property) is None:
                    property_dict[property]=[value]
                else:
                    if value not in property_dict[property]:
                        property_dict[property].append(value)
        return property_dict

    def get_all_variant_properties(self,obj):
        variants =  Variants.objects.filter(product = obj.product)
        property_dict = {}
        for variant in variants:
            options =  variant.variantoption.all()
            for option in options:
                option_values = option.property_value.all()
                for i in option_values:
                    property = i.property.property
                    value = i.values
                    if property_dict.get(property) is None:
                        property_dict[property]=[value]
                    else:
                        if value not in property_dict[property]:
                            property_dict[property].append(value)
        return property_dict    

    def get_variant_options(self,obj):

        return VariantOptionSerializers(obj.variantoption.all(), many=True).data
    
    def get_all_variant_options(self, obj):
        variants =  Variants.objects.filter(product = obj.product)
        options = []
        for variant in variants:
            options.append(VariantOptionSerializers(variant.variantoption.all(), many=True).data)
        return options

    def get_variants(self, obj):
        variants = ProductVariantsSerializers(Variants.objects.filter(product = obj.product), many = True).data
        return variants
    
    def get_main_img(self, obj):
        if Images.objects.filter(variant = obj).filter(is_main = True).exists():
            main_img = Images.objects.filter(variant = obj).filter(is_main = True).first() 
            return main_img.image.url
        return ''


    def get_images(self, obj):
        images = Images.objects.filter(variant = obj)
        images_path = []
        for i in images: 
            images_path.append(i.image.url)
        return images_path

    def get_url(self, obj):
    
        return obj.get_absolute_url()
    

class CategoryProductListSerializer(serializers.ModelSerializer):

    variant_product = serializers.SerializerMethodField()
    # variant_property  = serializers.SerializerMethodField()
    main_img = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Variants
        fields = (
            'title',
            'variant_product',
            'main_img',
            # 'variant_property',
            'stock',
            'price',
            'discount_type',
            'discount_amount',
            'actual_price',
            'url' 
        )

    def get_variant_product(self, obj):
        variant_product = {}
        variant_product['title'] = obj.product.title
        variant_product['brand'] = obj.product.brand
        variant_product['category'] = obj.product.category.title
        variant_product['status'] = obj.product.status
        variant_product['description'] = obj.product.description
        variant_product['detail'] = obj.product.detail

        return variant_product

    # def get_variant_property(self, obj):
    #     variant_values = obj.property_value.all()
    #     property_dict = {}
    #     for i in variant_values:
    #         property = i.property.property
    #         value = i.values
    #         if property_dict.get(property) is None:
    #             property_dict[property]=[value]
    #         elif value not in property_dict.get(property):
    #             property_dict[property].append(value)
    #     return property_dict


    
    def get_main_img(self, obj):
        if Images.objects.filter(variant = obj).filter(is_main = True).exists():
            main_img = Images.objects.filter(variant = obj).filter(is_main = True).first() 
            return main_img.image.url
        return ''


    def get_url(self, obj):
    
        return obj.get_absolute_url()
    

class ProductSearchSerializer(serializers.ModelSerializer):

    variant_product = serializers.SerializerMethodField()
    # variant_property = serializers.SerializerMethodField()
    main_img = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Variants
        fields = (
            'title',
            'variant_product',
            'main_img',
            # 'variant_property',
            'stock',
            'price',
            'discount_type',
            'discount_amount',
            'actual_price',
            'url' 
        )

    def get_variant_product(self, obj):
        variant_product = {}
        variant_product['title'] = obj.product.title
        variant_product['brand'] = obj.product.brand
        variant_product['category'] = obj.product.category.title
        variant_product['status'] = obj.product.status
        variant_product['description'] = obj.product.description
    
        return variant_product

    # def get_variant_property(self, obj):
    #     variant_values = obj.property_value.all()
    #     property_dict = {}
    #     for i in variant_values:
    #         property = i.property.property
    #         value = i.values
    #         if property_dict.get(property) is None:
    #             property_dict[property]=[value]
    #         elif value not in property_dict.get(property):
    #             property_dict[property].append(value)

        # return property_dict
    
    def get_main_img(self, obj):
        if Images.objects.filter(variant = obj).filter(is_main = True).exists():
            main_img = Images.objects.filter(variant = obj).filter(is_main = True).first() 
            return main_img.image.url
        return ''



    def get_url(self, obj):
    
        return obj.get_absolute_url()
    


