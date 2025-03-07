from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests


@dataclass
class WeatherData:
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    description: str
    timestamp: datetime


class WeatherService:
    """Service de gestion des données météorologiques"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_current_weather(
        self, latitude: float, longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Récupère les données météorologiques actuelles pour une localisation.

        Args:
            latitude: Latitude de la localisation
            longitude: Longitude de la localisation

        Returns:
            Dict contenant les données météo ou None en cas d'erreur
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric",  # Pour avoir les températures en Celsius
            }

            response = requests.get(self.base_url + "/weather", params=params)
            response.raise_for_status()

            weather_data = response.json()

            # Formater les données pour notre usage
            return {
                "temperature": weather_data.get("main", {}).get("temp"),
                "humidity": weather_data.get("main", {}).get("humidity"),
                "pressure": weather_data.get("main", {}).get("pressure"),
                "wind_speed": weather_data.get("wind", {}).get("speed"),
                "description": weather_data.get("weather", [{}])[0].get(
                    "description", ""
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"Erreur lors de la récupération des données météo: {str(e)}")
            return None

    def get_forecast(
        self, latitude: float, longitude: float, days: int = 7
    ) -> List[Dict]:
        """Obtient les prévisions météorologiques"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric",
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for item in data["list"][: days * 8]:  # 8 mesures par jour
                forecast = {
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "description": item["weather"][0]["description"],
                    "rain": item.get("rain", {"3h": 0}),
                    "timestamp": datetime.fromtimestamp(item["dt"]),
                }
                forecasts.append(forecast)

            return forecasts
        except Exception as e:
            print(f"Erreur lors de la récupération des prévisions: {str(e)}")
            return [self._get_default_weather() for _ in range(days)]

    def analyze_growing_conditions(
        self, latitude: float, longitude: float, crop_type: str
    ) -> Dict:
        """Analyse les conditions de croissance pour une culture spécifique"""
        current = self.get_current_weather(latitude, longitude)
        forecast = self.get_forecast(latitude, longitude)

        # Analyse basique des conditions
        conditions = {
            "temperature_suitable": 15 <= current["temperature"] <= 30,
            "humidity_suitable": 40 <= current["humidity"] <= 80,
            "wind_risk": current["wind_speed"] > 20,
            "rain_expected": any(f.get("rain", {}).get("3h", 0) > 0 for f in forecast),
            "frost_risk": any(f["temperature"] < 2 for f in forecast),
        }

        # Recommandations spécifiques selon la culture
        crop_recommendations = self._get_crop_recommendations(crop_type, conditions)

        return {
            "current_conditions": current,
            "forecast": forecast[:5],  # 5 premiers jours
            "analysis": conditions,
            "recommendations": crop_recommendations,
        }

    def _get_default_weather(self) -> Dict:
        """Retourne des données météo par défaut en cas d'erreur"""
        return {
            "temperature": 25.0,
            "humidity": 60.0,
            "wind_speed": 10.0,
            "description": "Pas de données disponibles",
            "rain": {"1h": 0},
            "timestamp": datetime.now().isoformat(),
        }

    def _get_crop_recommendations(self, crop_type: str, conditions: Dict) -> List[str]:
        """Génère des recommandations basées sur le type de culture et les conditions"""
        recommendations = []

        if not conditions["temperature_suitable"]:
            recommendations.append(
                "Température non optimale - surveillez de près la croissance"
            )

        if not conditions["humidity_suitable"]:
            recommendations.append("Humidité non optimale - ajustez l'irrigation")

        if conditions["wind_risk"]:
            recommendations.append("Risque de vent fort - prévoyez des protections")

        if conditions["rain_expected"]:
            recommendations.append(
                "Pluie prévue - planifiez les travaux en conséquence"
            )

        if conditions["frost_risk"]:
            recommendations.append("Risque de gel - préparez des mesures de protection")

        return recommendations
