from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Category, Order, Product, SellerProfile, User


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('title', 'price', 'approved', 'created_at')
    readonly_fields = ('created_at',)

class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'approved', 'registration_date', 'user_email', 'user_phone', 'user_address')
    inlines = [ProductInline]
    search_fields = ('user__username', 'user__email')
    list_filter = ('approved',)

    def user_email(self, obj):
        return obj.user.email
    def user_phone(self, obj):
        return obj.user.phone
    def user_address(self, obj):
        return obj.user.address
    user_email.short_description = 'Email'
    user_phone.short_description = 'Phone'
    user_address.short_description = 'Address'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'displayed_price', 'approved', 'created_at')
    list_filter = ('approved', 'category')
    search_fields = ('title', 'seller__username')
    readonly_fields = ('created_at', 'updated_at')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'buyer_name', 'buyer_phone', 'buyer_email', 'created_at', 'processed')
    list_filter = ('processed', 'created_at')
    search_fields = ('buyer_name', 'buyer_phone', 'buyer_email', 'product__title')
    readonly_fields = ('created_at',)

    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'approved', 'registration_date')

admin.site.register(User, UserAdmin)
admin.site.register(SellerProfile, SellerProfileAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)