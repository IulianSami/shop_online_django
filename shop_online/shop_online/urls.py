"""shop_online URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# shop_online/urls.py



from django.contrib import admin
from django.urls import path, include
from store import views  
from django.contrib.auth import views as auth_views  # Import auth_views for LogoutView
from django.conf import settings
from django.conf.urls.static import static
from store import urls as store_urls




urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # URL for logging out
    path('', views.home, name='home'),  # Root URL, directs to home view in views.py
    path('store/', include('store.urls', namespace='store')),  # Includes the URL patterns defined in the store app
    path('accounts/', include('django.contrib.auth.urls')),  # URLs for authentication (login, password reset, ...)
    path('accounts/signup/', views.signup, name='signup'),  # URL for the user registration page
    path('terms/', views.agree_terms_and_conditions, name='agree_terms_and_conditions'),
    
    
    
    
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
