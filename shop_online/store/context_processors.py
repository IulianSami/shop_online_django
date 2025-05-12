# store/context_processors.py   (for red dott with number of items in cart)
from .models import Cart, CartItem

def cart_item_count(request):
    """Add number of products in the cart to the context."""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_ordered=False).first()
        if cart:
            item_count = sum(item.quantity for item in cart.items.all())
        else:
            item_count = 0
    else:
        item_count = 0
    return {'item_count': item_count}