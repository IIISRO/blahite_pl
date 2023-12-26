from django.contrib import admin
from .models import User, Address, Basket

# Register your models here.


admin.site.register(Address)

class UserAdressInline(admin.TabularInline):
    model = Address
    extra = 1
    show_change_link = True

class UserAdmin(admin.ModelAdmin):
    inlines = [UserAdressInline]

admin.site.register(User,UserAdmin)
admin.site.register(Basket)
