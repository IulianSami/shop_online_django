from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import requests

def weather_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
        return JsonResponse({'error': 'User not authenticated or no profile'}, status=401)
    
    city = request.user.profile.city
    if not city:
        return JsonResponse({'error': 'No city set in profile. Please set your city.'}, status=400)
    
    try:
        api_key = settings.WEATHER_API_KEY
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            return JsonResponse({'error': data.get('message', 'Weather data unavailable')}, status=400)
        
        # Sending weather data to template
        context = {
            'city': city,
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind': data['wind']['speed'],
        }
        return render(request, 'store/weather.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
