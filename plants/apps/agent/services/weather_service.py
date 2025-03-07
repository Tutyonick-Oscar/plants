from datetime import datetime, timedelta
from typing import Dict, List

import requests
from pydantic import BaseModel


class WeatherForecast(BaseModel):
    date: datetime
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    description: str


class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Effectue une requête à l'API avec gestion des erreurs"""
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête API: {e}")
            return None

    def get_current_weather(self, lat: float, lon: float) -> WeatherForecast:
        """Obtient les conditions météorologiques actuelles"""
        endpoint = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr",
        }

        data = self._make_request(endpoint, params)

        return WeatherForecast(
            date=datetime.now(),
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            precipitation=data.get("rain", {}).get("1h", 0),
            wind_speed=data["wind"]["speed"],
            description=data["weather"][0]["description"],
        )

    def get_short_term_forecast(self, lat: float, lon: float) -> List[WeatherForecast]:
        """Obtient les prévisions à court terme (48 heures)"""
        endpoint = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr",
        }

        data = self._make_request(endpoint, params)
        forecasts = []

        try:
            for item in data.get("list", [])[:16]:
                forecasts.append(
                    WeatherForecast(
                        date=datetime.fromtimestamp(item["dt"]),
                        temperature=item["main"]["temp"],
                        humidity=item["main"]["humidity"],
                        precipitation=item.get("rain", {}).get("3h", 0),
                        wind_speed=item["wind"]["speed"],
                        description=item["weather"][0]["description"],
                    )
                )
        except (KeyError, IndexError) as e:
            print(f"Erreur lors du parsing des prévisions: {e}")
            # Ajouter une prévision par défaut
            forecasts.append(self.get_current_weather(lat, lon))

        return forecasts

    def analyze_growing_conditions(
        self, lat: float, lon: float, crop_type: str
    ) -> Dict:
        """Analyse les conditions de croissance pour une culture spécifique"""
        current = self.get_current_weather(lat, lon)
        forecasts = self.get_short_term_forecast(lat, lon)

        # Analyse des conditions pour le maïs
        if crop_type.lower() == "maïs":
            return self._analyze_corn_conditions(current, forecasts)

        # Par défaut, retourner une analyse générique
        return self._analyze_generic_conditions(current, forecasts)

    def _analyze_corn_conditions(
        self, current: WeatherForecast, forecasts: List[WeatherForecast]
    ) -> Dict:
        """Analyse spécifique pour le maïs"""
        temp_avg = sum(f.temperature for f in forecasts) / len(forecasts)
        precip_total = sum(f.precipitation for f in forecasts)

        analysis = {
            "score_global": 0,
            "risques_immediats": [],
            "conditions_favorables": [],
            "recommandations": [],
        }

        # Température
        if temp_avg < 10:
            analysis["risques_immediats"].append(
                "Température trop basse pour la croissance du maïs"
            )
            analysis["recommandations"].append("Envisager de retarder la plantation")
        elif temp_avg > 35:
            analysis["risques_immediats"].append("Risque de stress thermique")
            analysis["recommandations"].append("Prévoir une irrigation supplémentaire")
        else:
            analysis["conditions_favorables"].append("Température favorable")

        # Précipitations
        if precip_total < 10:
            analysis["risques_immediats"].append("Risque de sécheresse")
            analysis["recommandations"].append("Planifier l'irrigation")
        elif precip_total > 50:
            analysis["risques_immediats"].append("Risque d'excès d'eau")
            analysis["recommandations"].append("Vérifier le drainage")
        else:
            analysis["conditions_favorables"].append("Précipitations adéquates")

        # Score global (0-100)
        temp_score = min(100, max(0, (temp_avg - 10) * 5))
        precip_score = min(100, max(0, precip_total / 2))
        analysis["score_global"] = (temp_score + precip_score) / 2

        return analysis

    def _analyze_generic_conditions(
        self, current: WeatherForecast, forecasts: List[WeatherForecast]
    ) -> Dict:
        """Analyse générique pour toute culture"""
        temp_avg = sum(f.temperature for f in forecasts) / len(forecasts)
        precip_total = sum(f.precipitation for f in forecasts)

        analysis = {
            "score_global": 0,
            "risques_immediats": [],
            "conditions_favorables": [],
            "recommandations": [],
        }

        # Température
        if temp_avg < 5:
            analysis["risques_immediats"].append("Risque de gel")
        elif temp_avg > 30:
            analysis["risques_immediats"].append("Risque de chaleur excessive")
        else:
            analysis["conditions_favorables"].append("Température modérée")

        # Précipitations
        if precip_total < 5:
            analysis["risques_immediats"].append("Conditions sèches")
        elif precip_total > 40:
            analysis["risques_immediats"].append("Risque d'excès d'eau")
        else:
            analysis["conditions_favorables"].append("Précipitations modérées")

        # Score global (0-100)
        temp_score = min(100, max(0, 100 - abs(temp_avg - 20) * 5))
        precip_score = min(100, max(0, 100 - abs(precip_total - 20) * 2))
        analysis["score_global"] = (temp_score + precip_score) / 2

        return analysis
