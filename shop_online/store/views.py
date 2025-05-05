from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import SignUpForm, ProfileForm, ReviewForm
from .models import Cart, CartItem, OrderItem, Product, Order, Category, Review
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.conf import settings
from django.db import IntegrityError
import requests
from django.contrib.auth.views import LoginView
from .models import Profile
from django.core.mail import send_mail
#from .forms import ContactForm  # if use form Django








def get_authenticated_weather(request):
    if request.user.is_authenticated:
        city = get_user_city(request)
        return get_weather_data(city)
    return {'weather': {}, 'weather_error': None}


# Helper function to fetch weather data from OpenWeatherMap API
def get_weather_data(city):
    if not city:
        return {'weather': {}, 'weather_error': 'No city provided'}

    api_key = settings.WEATHER_API_KEY
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}'
    weather_data = {}
    error = None
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        if data.get('cod') == 200:  # Verify if return code is 200
            weather_data = {
                'city': city,
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind': data['wind']['speed'],
                'pressure': data['main'].get('pressure', 'N/A'),
            }
        else:
            error = data.get('message', 'Weather data unavailable')

    except requests.exceptions.RequestException as e:
        # Error networking or connection issues
        error = f'Failed to connect to weather API: {str(e)}'
    except (KeyError, ValueError) as e:
        # Error at interpretation of JSON answer
        error = f'Failed to parse weather data: {str(e)}'

    return {'weather': weather_data, 'weather_error': error}


# Helper function to get city from authenticated user's profile
def get_user_city(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        # Verify if user has profile & city set
        return getattr(request.user.profile, 'city', None)  # Returnăm orașul setat în profilul utilizatorului
    return None  # No profile or user not logged in , return None .




# View for product search by keyword in name or description
def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )
    weather = get_authenticated_weather(request)
 
    return render(request, 'store/product_list.html', {
        'page_obj': products,
        'query': query,
        'weather': weather['weather'],
        'weather_error': weather['weather_error'],
    })


# Homepage view that shows weather information
def home(request):
    weather = get_weather_data(get_user_city(request)) 
    return render(request, 'store/home.html', {
        'weather': weather['weather'],
        'weather_error': weather['weather_error'],
    })



# Another homepage/index variant
def index(request):
    weather = get_authenticated_weather(request) 
    return render(request, 'store/index.html', {
        'weather': weather['weather'],
        'weather_error': weather['weather_error'],
    })


# Product list with filters: price range, stock availability, category, search query
def product_list(request):
    products = Product.objects.all()
    price_range = request.GET.get('price_range')
    stock_filter = request.GET.get('stock')
    category_name = request.GET.get('category')
    query = request.GET.get('q', '')


    # Fetch all categories
    categories = Category.objects.all()

    
    # Filters for price range
    if price_range:
        if price_range == '0-100':
            products = products.filter(price__gte=0, price__lte=100)
        elif price_range == '100-500':
            products = products.filter(price__gt=100, price__lte=500)
        elif price_range == '500-1000':
            products = products.filter(price__gt=500, price__lte=1000)
        elif price_range == '1000+':
            products = products.filter(price__gt=1000)

    # Filters for stock availability
    if stock_filter:
        if stock_filter == 'in_stock':
            products = products.filter(stock__gt=0)
        elif stock_filter == 'low_stock':
            products = products.filter(stock__lt=5, stock__gt=0)

    # Filters for category
    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass

    # Filters for search query
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # Sort products by name
    products = products.order_by('name')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Creates a dictionary to check if the user has purchased the product
    has_purchased = {}
    if request.user.is_authenticated:
        # Verify if user has purchased products
        orders = Order.objects.filter(user=request.user)
        purchased_product_ids = OrderItem.objects.filter(order__in=orders).values_list('product_id', flat=True)
        purchased_products = Product.objects.filter(id__in=purchased_product_ids)

        # Create a dictionary to check if the user has purchased each product
        for product in products:
            has_purchased[product.id] = product in purchased_products

    # Obtain weather data for the authenticated user
    weather = get_authenticated_weather(request)
    print("Orașul utilizatorului:", get_user_city(request))
    print("Date meteo:", weather)

    # Returns the product list template with context
    return render(request, 'store/product_list.html', {
        'page_obj': page_obj,
        'message': request.GET.get('message', ''),
        'active_price_range': price_range,
        'active_stock_filter': stock_filter,
        'active_category': category_name,
        'search_query': query,
        'weather': weather['weather'],  
        'weather_error': weather.get('error', None),  
        'has_purchased': has_purchased,  
    })



# Cart view: shows items, calculates total
@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        items = cart.items.all()
        total = sum(item.get_total_price() for item in items)
    else:
        items = []
        total = 0

    weather = get_authenticated_weather(request) 

    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'weather': weather['weather'],
        'weather_error': weather['weather_error'],
    })




# Helper function to create a profile if one doesn't exist
def create_user_profile(user):
    
    if not Profile.objects.filter(user=user).exists():
        try:
            profile = Profile(user=user)
            profile.save()
        except IntegrityError:
            print(f"Profilul pentru utilizatorul {user.username} există deja.")
    else:
        print(f"Profilul pentru utilizatorul {user.username} există deja.")


# User registration view with custom profile form
def signup(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.is_superuser = False
            user.is_staff = False
            user.save()

            # Not create profile here, but in the CustomLoginView
            # create_user_profile(user)  # Create profile if it doesn't exist
            profile = user.profile
            profile.city = profile_form.cleaned_data.get('city')
            profile.phone_number = profile_form.cleaned_data.get('phone_number')
            profile.birth_date = profile_form.cleaned_data.get('birth_date')
            profile.address = profile_form.cleaned_data.get('address')
            profile.save()

            messages.success(request, 'Your account was created successfully!')
            return redirect('login')
        else:
            # Print errors for debugging
            print("Errors user_form:", user_form.errors)
            print("Errors profile_form:", profile_form.errors)

    else:
        user_form = SignUpForm()
        profile_form = ProfileForm()

    return render(request, 'store/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# View showing checkout page with item validation and weather info
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('store:cart_view')

    items = cart.items.all()
    total = sum(item.get_total_price() for item in items)

    has_zero_stock = any(item.product.stock <= 0 for item in items)
    if has_zero_stock:
        return redirect('store:cart_view')

    weather = get_authenticated_weather(request) 

    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total,
        'weather': weather['weather'],
        'weather_error': weather['weather_error'],
    })



# Checkout logic that updates stock and clears cart after order is placed
@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        items = cart.items.all()
        total = sum(item.get_total_price() for item in items)

        for item in items:
            product = item.product
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()
            else:
                messages.error(request, f"Insufficient stock for {product.name}")
                return redirect('store:cart_view')

        cart.items.all().delete()
        return redirect('store:thank_you')
    else:
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'items': [],
            'total': 0
        })


#   Simple "Thank You" page after placing an order!
def thank_you(request):
    weather = get_authenticated_weather(request) 
    return render(request, 'store/thank_you.html', {
        'weather': weather['weather'],
        'weather_error': weather['weather_error'],
    })



# Adds a product to user's cart; creates cart/cartitem if needed
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user, is_ordered=False)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('store:cart_view')



# Removes a specific item from the user's cart
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if cart_item.cart.user == request.user:
        cart_item.delete()
    return redirect('store:cart_view')



# Updates quantity for a cart item, checks stock availability
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        if quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Quantity for {cart_item.product.name} has been updated!")
        else:
            messages.error(request, f"Insufficient stock for {cart_item.product.name}.")

    # Redirecționare după actualizare
    return redirect('store:cart_view')



# Handles placing an order from the cart
def place_order_view(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return redirect('store:cart_view')

        order = Order.objects.create(user=request.user, total_price=cart.get_total_price())

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # update stock
            product = item.product
            product.stock -= item.quantity
            product.save()

        cart.items.all().delete()

        return redirect('store:order_confirmation', order_id=order.id)

    weather = get_authenticated_weather(request) 
    return render(request, 'store/cart.html', {'weather': weather['weather'], 'weather_error': weather['weather_error']})




# Confirmation page after successful order placement
def order_confirmation_view(request, order_id):
    order = Order.objects.get(id=order_id)

    # Obtain items for the order
    order_items = order.items.all()

    # Obtain weather data for the authenticated user
    weather = get_authenticated_weather(request) 

    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'order_items': order_items,  # Add order items to context
        'weather': weather['weather'],
        'weather_error': weather['weather_error'],
    })


# API endpoint returning weather data as JSON for logged-in user's city
def weather_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
        return JsonResponse({'error': 'User not authenticated or no profile'}, status=401)
    
    # Use city from request or from user's profile
    city = request.GET.get('city', None)
    if not city:
        city = request.user.profile.city if hasattr(request.user, 'profile') else None
    
    if not city:
        return JsonResponse({'error': 'No city provided or set in profile.'}, status=400)


    # Continue with API call to OpenWeatherMap

    try:
        api_key = settings.WEATHER_API_KEY
        # https://home.openweathermap.org/users/sign_in  (register/ take a free key for API)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return JsonResponse({'error': data.get('message', 'Weather data unavailable')}, status=400)

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



# View for updating user profile (e.g. city for weather)
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('store:home')
    else:
        form = ProfileForm(instance=request.user.profile)

    weather = get_authenticated_weather(request) 
    return render(request, 'store/update_profile.html', {'form': form, 'weather': weather['weather'], 'weather_error': weather['weather_error']})





# Custom login view to ensure user profile is created upon login if missing
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        
        if user is not None:
            login(self.request, user)
            
           
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                
                profile = Profile(user=user)
                profile.save()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


# Autodisconnect if user/admin does nothing on website for 30 minute
def custom_logout(request):
    logout(request)
    return redirect('store:home')  # Redirect to home page after logout

    




# Contact form view to send email to admin
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"Contact Message from {name}"
        message_body = f"Message from {name} ({email}):\n\n{message}"
        admin_email = 'iuliansami@gmail.com'

        try:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('store:contact')
        except Exception as e:
            messages.error(request, 'There was an error sending your message. Please try again later.')
            return redirect('store:contact')
    else:
        return render(request, 'store/contact.html')


# Email testing
def test_email(request):
    send_mail(
        'Test Subject',
        'Test Message',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,
    )
    return HttpResponse('Email sent successfully!')


#Review view for product detail page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(
            user=request.user,
            items__product=product
        ).exists()

    # Define the form for leaving a review
    form = ReviewForm()  # Create an empty form instance

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been added successfully!")
            return redirect('store:product_detail', product_id=product.id)

    reviews = product.reviews.all()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,  # Send the form to the template
        'has_purchased': has_purchased,
    })


def leave_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been added successfully!')
            return redirect('store:product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'store/leave_review.html', {
        'form': form,
        'product': product
    })
