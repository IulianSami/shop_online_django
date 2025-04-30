// Așteaptă ca documentul să fie complet încărcat
document.addEventListener('DOMContentLoaded', function () {
    const weatherContainer = document.getElementById('weather-data');
    
    // Mesaj inițial dacă utilizatorul nu are setat un oraș
    weatherContainer.innerHTML = `
        <p>Please set your city in profile to see weather</p>
    `;

    // Verifică dacă utilizatorul este autentificat și are un oraș setat
    const userCity = getUserCity(); // Presupunem că există o funcție care returnează orașul utilizatorului

    if (userCity) {
        fetchWeather(userCity);
    }

    // Funcție pentru a aduce datele meteo
    async function fetchWeather(city) {
        try {
            // Realizează cererea la serverul Django
            const response = await fetch(`/weather/?city=${encodeURIComponent(city)}`);
            const data = await response.json();
            
            if (data.error) {
                showWeatherError(data.error);
                return;
            }

            updateWeatherUI(data);
        } catch (error) {
            showWeatherError('Failed to load weather data');
            console.error('Weather fetch error:', error);
        }
    }

    // Funcție pentru a actualiza UI-ul cu informațiile meteo
    function updateWeatherUI(data) {
        weatherContainer.innerHTML = `
            <p>Temperature: ${Math.round(data.main.temp)}°C</p>
            <p>Weather: ${data.weather[0].description}</p>
            <p>Humidity: ${data.main.humidity}%</p>
            <p>Wind Speed: ${data.wind.speed} m/s</p>
            <p>Feels Like: ${Math.round(data.main.feels_like)}°C</p>
        `;
    }

    // Funcție pentru a arăta eroare în UI
    function showWeatherError(message) {
        weatherContainer.innerHTML = `<p>${message}</p>`;
    }

    // Funcție pentru a obține iconița corespunzătoare vremii
    function getWeatherIcon(weatherMain) {
        const icons = {
            'Clear': 'fas fa-sun',
            'Clouds': 'fas fa-cloud',
            'Rain': 'fas fa-cloud-rain',
            'Drizzle': 'fas fa-cloud-rain',
            'Thunderstorm': 'fas fa-bolt',
            'Snow': 'fas fa-snowflake',
            'Mist': 'fas fa-smog',
            'Smoke': 'fas fa-smog',
            'Haze': 'fas fa-smog',
            'Fog': 'fas fa-smog'
        };
        
        return icons[weatherMain] || 'fas fa-cloud-sun';
    }

    // O funcție care să returneze orașul utilizatorului
    function getUserCity() {
        // Presupunem că orașul este stocat într-un profil al utilizatorului
        // Poți înlocui această funcție cu logica ta reală de a obține orașul
        return "London"; // Exemplu: orașul utilizatorului
    }
});
