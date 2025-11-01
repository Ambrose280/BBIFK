from django.contrib import admin
from .models import Address, Category, Product, Cart, Order
import admin_thumbnails
from django.utils.html import mark_safe

admin.site.site_header = "Prince Luxury Admin"
admin.site.site_title = "Prince SOJ Dashboard"
admin.site.index_title = "Welcome to the Control Panel"

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')



class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category_image_url', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title", )}

    def category_image_thumb(self, obj):
        """Renders a clickable product image preview from Cloudinary."""
        if obj.category_image_url:
            return mark_safe(
                f'<a href="{obj.category_image_url}" target="_blank">'
                f'<img src="{obj.category_image_url}" '
                f'style="height:60px;border-radius:6px;object-fit:cover;" /></a>'
            )
        return "—"
    category_image_thumb.short_description = "Preview"
    


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'product_image_thumb', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'category', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'category', 'short_description')
    prepopulated_fields = {"slug": ("title", )}
    
    def product_image_thumb(self, obj):
        """Renders a clickable product image preview from Cloudinary."""
        if obj.product_image_url:
            return mark_safe(
                f'<a href="{obj.product_image_url}" target="_blank">'
                f'<img src="{obj.product_image_url}" '
                f'style="height:60px;border-radius:6px;object-fit:cover;" /></a>'
            )
        return "—"
    product_image_thumb.short_description = "Preview"

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'ordered_date')
    list_editable = ('quantity', 'status')
    list_filter = ('status', 'ordered_date')
    list_per_page = 20
    search_fields = ('user', 'product')


admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)