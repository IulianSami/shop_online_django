# store/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Model representing a product category
class Category(models.Model):
    name = models.CharField(max_length=100)  # Name of the category
    description = models.TextField()  # Description of the category

    class Meta:
        verbose_name = "Category"  # Singular display name in the admin
        verbose_name_plural = "Categories"  # Plural display name in the admin

    def __str__(self):     
        return self.name   # Returns the name when the object is printed


# Model representing a product
class Product(models.Model):
    ELECTRONICS = 'Electronics'  # Choice value for electronics
    ELECTRICS = 'Electrics'  # Choice value for electrics
    
    CATEGORY_CHOICES = [
        (ELECTRONICS, 'Electronics'),   # Tuple for electronics choice
        (ELECTRICS, 'Electrics'),  # Tuple for electrics choice
    ]
    
    name = models.CharField(max_length=200)  # Product name
    description = models.TextField()  # Product description
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00   # Default price
    )
    stock = models.PositiveIntegerField(default=0)  # Product stock
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True  # Product can have no category
    )
    category_type = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True  # Optional additional category type
    )
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # Optional product image
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when product was created

    # Rating field for product reviews
    rating = models.FloatField(default=0.0)  # Adăugăm câmpul rating

    def __str__(self):
        return self.name  # Returns product name when printed


    @property
    def in_stock(self):
        return self.stock > 0  # Check if product is in stock

    @property
    def is_low_stock(self):
        return 0 < self.stock < 5  # Check if product stock is low


# Model representing a shopping cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')  # One cart per user
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp when cart was created
    is_ordered = models.BooleanField(default=False)  # Indicates if cart has been ordered

    def __str__(self):
        return f"Cart of {self.user.username}"  # String representation of the cart

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())  # Sum of all item prices in the cart


# Model representing a cart item
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)  # Reference to the cart
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Reference to the product
    quantity = models.PositiveIntegerField(default=1)  # Quantity of product in the cart

    def __str__(self):
        # Show product, quantity, price and total
        total_price = self.get_total_price()
        return f"{self.product.name} - {self.quantity} x {self.product.price} = {total_price}"

    def get_total_price(self):
        # Calculate total price based on quantity and unit price
        return self.product.price * self.quantity
    
    
# Model representing a finalized order
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who made the order
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total price of the order
    created_at = models.DateTimeField(auto_now_add=True)  # Order creation time
    updated_at = models.DateTimeField(auto_now=True)  # Last time the order was updated
    # items = models.ManyToManyField('CartItem')  # Items included in the order

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"  # String representation of the order
    

# Model representing a user profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One profile per user
    city = models.CharField(max_length=100, blank=True, null=True)  # User's city, optional~
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    
    def __str__(self):
        return self.user.username  # Display the username as profile name
    


# Signal to automatically create or update Profile when a User is saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  # Create profile when user is created
    else:
        instance.profile.save()  # Save existing profile when user is updatedpython 


# Review model for product reviews
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')  # tightly coupled with product
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # tightly coupled with user
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rate 1-5 stars
    text = models.TextField()  # Text of the review
    created_at = models.DateTimeField(auto_now_add=True)  # Date when review was created

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
    


# Model for items in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)  # 
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Buying product
    quantity = models.PositiveIntegerField()  # Quantity of product in the order
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit at the time of order

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.price}"

    def get_total_price(self):
        return self.quantity * self.price  # Price of the order item
    

# Model for Footer Newsletter Subscription
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email