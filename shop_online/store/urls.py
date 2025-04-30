from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'store'  # Add this line to set the app namespace


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alt'),
    path('index/', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('search/', views.product_list, name='search_products'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('place_order/', views.place_order_view, name='place_order'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('weather/', views.weather_view, name='weather'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('contact/', views.contact, name='contact'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
]
