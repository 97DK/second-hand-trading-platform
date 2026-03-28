from django.contrib import admin
from .models import Product, WishItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'status', 'dormitory_building')
    list_filter = ('category', 'status', 'dormitory_building')
    search_fields = ('title', 'seller__student_id')

@admin.register(WishItem)
class WishItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'max_price', 'is_fulfilled')
    list_filter = ('is_fulfilled',)