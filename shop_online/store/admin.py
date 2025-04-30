from django.contrib import admin
from django.utils.translation import gettext_lazy as _  # Import translation utility for multilingual support
from django.utils.html import format_html  # Import HTML formatting utility
from .models import Product, Category, Cart, CartItem, Profile, Review  # Import the models to register them in the admin panel

# Custom filter for stock status
class StockFilter(admin.SimpleListFilter):
    title = _('Stock Status')  # Title of the filter in the admin panel
    parameter_name = 'stock'  # Query parameter for the filter

    # Define the filter options
    def lookups(self, request, model_admin):
        return (
            ('in_stock', _('In Stock')),  # Filter option for products in stock
            ('low_stock', _('Low Stock (<5)'),),  # Filter option for products with stock less than 5
            ('out_of_stock', _('Out of Stock')),  # Filter option for products out of stock
        )

    # Filter query logic
    def queryset(self, request, queryset):
        if self.value() == 'in_stock':  # If the filter is "in stock"
            return queryset.filter(stock__gt=0)  # Return products where stock is greater than 0
        if self.value() == 'low_stock':  # If the filter is "low stock"
            return queryset.filter(stock__lt=5, stock__gt=0)  # Return products with stock between 0 and 5
        if self.value() == 'out_of_stock':  # If the filter is "out of stock"
            return queryset.filter(stock=0)  # Return products with 0 stock

# Custom filter for creation date
class DateCreatedFilter(admin.DateFieldListFilter):
    title = _('Creation Date')  # Title of the filter in the admin panel
    parameter_name = 'created_at'  # Query parameter for the filter

# Category model admin configuration
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Display category name and description in the admin list
    search_fields = ('name',)  # Enable search by category name

# Product model admin configuration
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'formatted_created_at', 'image_tag')  # Columns displayed in the product list
    list_filter = (
        StockFilter,  # Custom filter for stock status
        'category',  # Filter by category
        ('created_at', DateCreatedFilter),  # Filter by creation date using the custom filter
    )
    search_fields = ('name', 'description')  # Enable search by product name and description
    ordering = ('-created_at',)  # Order products by creation date, descending
    readonly_fields = ('image_tag',)  # Make image_tag field read-only

    # Display product image as a thumbnail in the admin list
    def image_tag(self, obj):
        if obj.image:  # If the product has an image
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)  # Display image with fixed size
        return _("No Image")  # If there is no image, return a placeholder text
    image_tag.short_description = _('Image Preview')  # Set the column title for image preview

    # Display product creation date in a specific format
    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d %b %Y')  # Format the creation date as day-month-year
    formatted_created_at.short_description = _('Created At')  # Set column title
    formatted_created_at.admin_order_field = 'created_at'  # Enable ordering by creation date

# Cart model admin configuration
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_ordered')  # Display user, creation date, and order status
    search_fields = ('user__username',)  # Enable search by username in cart
    list_filter = ('is_ordered', 'created_at')  # Filter by order status and creation date

# CartItem model admin configuration
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')  # Display cart, product, quantity, and total price
    search_fields = ('cart__user__username', 'product__name')  # Enable search by username in cart and product name

    # Calculate and display total price for each cart item
    def total_price(self, obj):
        return f"${obj.product.price * obj.quantity:.2f}"  # Calculate total price as product price * quantity
    total_price.short_description = _('Total Price')  # Set column title for total price




# Profile model admin configuration
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'phone_number', 'birth_date', 'address')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'city')
        }),
        ('Additional Information', {
            'fields': ('phone_number', 'birth_date', 'address'),
        }),
    )



# Review model admin configuration
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('product', 'rating')