from django.contrib import admin
import admin_thumbnails
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product, Images, Variants, Property, PropertyValue, Options



# Register your models here.








@admin_thumbnails.thumbnail('image')
class CategoryAdmin2(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'



class VariantOptionsAdmin(admin.ModelAdmin):
    list_display = ['image_tag']
    readonly_fields = ('image_tag',)





class ProductVariantsInline(admin.TabularInline):
    model = Variants
    readonly_fields = ('actual_price',)
    extra = 1
    show_change_link = True

class OptionsInline(admin.TabularInline):
    model = Options
    readonly_fields = ('image_tag',)
    extra = 1

@admin_thumbnails.thumbnail('image')
class VariantsImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1

class VariantsAdmin(admin.ModelAdmin):
    list_display = ['title','product','price','image_tag']
    inlines = [VariantsImageInline,OptionsInline]
    readonly_fields = ('actual_price',)
    prepopulated_fields = {'slug': ('title',)}



@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image_thumbnail', 'variant', 'is_main']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','category','image_tag']
    list_filter = ['category']
    readonly_fields = ('image_tag',)
    inlines = [ProductVariantsInline]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Property)
class property(admin.ModelAdmin):
    search_fields = ['property']

@admin.register(PropertyValue)
class propertyvalue(admin.ModelAdmin):
    search_fields = ['values']



admin.site.register(Category,CategoryAdmin2)
admin.site.register(Product,ProductAdmin)
admin.site.register(Images,ImagesAdmin)
admin.site.register(Variants,VariantsAdmin)   
admin.site.register(Options,VariantOptionsAdmin)











