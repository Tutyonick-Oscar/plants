import re
from datetime import datetime
from typing import Any, Dict, Optional

import google.generativeai as genai

from plants.apps.agent.agents.base_agent import BaseAgent


class SoilAnalysisService(BaseAgent):
    """Service d'analyse des sols utilisant l'IA."""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def get_soil_requirements(self, crop_type: str, location: str) -> Dict[str, Any]:
        """Obtient les exigences du sol pour une culture spécifique.

        Args:
            crop_type: Type de culture
            location: Localisation du projet

        Returns:
            Dict contenant les exigences du sol
        """
        prompt = f"""En tant qu'expert en agronomie, générez les exigences détaillées du sol au format JSON pour la culture de {crop_type}
        dans la localisation {location}.

        Le format JSON doit suivre exactement cette structure :
        {{
            "ph_optimal": "plage de pH optimal",
            "texture": "texture idéale du sol",
            "matiere_organique": "pourcentage recommandé",
            "drainage": "niveau de drainage requis",
            "nutriments": {{
                "azote": "besoins en kg/ha",
                "phosphore": "besoins en kg/ha",
                "potassium": "besoins en kg/ha",
                "oligo_elements": ["liste des oligo-éléments nécessaires"]
            }},
            "preparation": ["étapes de préparation recommandées"],
            "amendements": ["amendements suggérés"],
            "analyses_recommandees": ["analyses à effectuer"]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            return self.parse_json_response(response.text)
        except Exception as e:
            return self._get_default_soil_requirements()

    def _get_default_soil_requirements(self) -> Dict[str, Any]:
        """Retourne des exigences de sol par défaut"""
        return {
            "timestamp": datetime.now().isoformat(),
            "ph_optimal": "6.0-7.5",
            "texture": "À déterminer",
            "matiere_organique": "À déterminer",
            "drainage": "À déterminer",
            "nutriments": {
                "azote": "À déterminer",
                "phosphore": "À déterminer",
                "potassium": "À déterminer",
                "oligo_elements": [],
            },
            "preparation": [],
            "amendements": [],
            "analyses_recommandees": [],
        }

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extrait une valeur numérique d'une chaîne de texte.

        Args:
            text: Texte contenant une valeur numérique

        Returns:
            float ou None si aucune valeur n'est trouvée
        """
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return float(numbers[0]) if numbers else None
