from typing import Dict, Any, Optional, List
import google.generativeai as genai
from datetime import datetime
import json
import re
from plants.apps.agent.agents.base_agent import BaseAgent

class CropManagementService(BaseAgent):
    """Service de gestion des cultures."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def get_crop_management_plan(self, crop_type: str, area: float, location: str) -> Dict[str, Any]:
        """Obtient le plan de gestion des cultures.
        
        Args:
            crop_type: Type de culture
            area: Surface en hectares
            location: Localisation du projet
            
        Returns:
            Dict contenant le plan de gestion
        """
        prompt = f"""En tant qu'expert en agronomie, générez un plan de gestion détaillé au format JSON pour la culture de {crop_type} 
        sur une surface de {area} hectares dans la localisation de {location}.

        Le plan doit suivre exactement cette structure JSON :
        {{
            "densite_semis": "valeur en plants/ha",
            "espacement": "distance entre rangs x distance entre plants",
            "profondeur_semis": "profondeur en cm",
            "irrigation": {{
                "besoin_total": "quantité en mm/saison",
                "frequence": "intervalle en jours",
                "methode": "méthode d'irrigation"
            }},
            "fertilisation": {{
                "base": {{
                    "NPK": "quantité en kg/ha",
                    "periode": "moment d'application"
                }},
                "couverture": {{
                    "type": "quantité en kg/ha",
                    "periodes": ["période 1", "période 2"]
                }}
            }},
            "traitements": {{
                "herbicides": {{
                    "pre_levee": "dose en L/ha",
                    "post_levee": "dose en L/ha"
                }},
                "insecticides": "recommandation"
            }}
        }}

        Important :
        1. Adaptez les quantités à la surface spécifiée
        2. Tenez compte de la localisation pour les recommandations
        3. Fournissez uniquement le JSON, sans texte avant ou après
        4. Assurez-vous que toutes les valeurs sont réalistes et applicables
        """
        
        response = self.model.generate_content(prompt)
        return self.parse_json_response(response.text)
    
    def generate_irrigation_schedule(self, crop_data: Dict[str, Any], climate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un calendrier d'irrigation optimisé"""
        
        prompt = f"""En tant qu'expert en irrigation, générez un calendrier d'irrigation détaillé basé sur les données suivantes :

Données de la culture :
{json.dumps(crop_data, indent=2)}

Données climatiques :
{json.dumps(climate_data, indent=2)}

Fournissez :
1. Besoins en eau quotidiens
2. Fréquence d'irrigation
3. Durée des sessions
4. Méthodes d'irrigation recommandées
5. Ajustements selon le stade de croissance
6. Monitoring et indicateurs
7. Mesures d'économie d'eau

Format de réponse souhaité : JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            schedule = self._parse_irrigation_schedule(response.text)
            return schedule
        except Exception as e:
            print(f"Erreur lors de la génération du calendrier d'irrigation: {str(e)}")
            return self._get_default_irrigation_schedule()
    
    def generate_fertilization_plan(self, soil_data: Dict[str, Any], crop_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un plan de fertilisation personnalisé"""
        
        prompt = f"""En tant qu'expert en fertilisation, générez un plan de fertilisation détaillé basé sur :

Données du sol :
{json.dumps(soil_data, indent=2)}

Besoins de la culture :
{json.dumps(crop_requirements, indent=2)}

Fournissez :
1. Types d'engrais recommandés
2. Doses par application
3. Calendrier d'application
4. Méthodes d'application
5. Ajustements selon le stade
6. Monitoring de la fertilité
7. Pratiques durables

Format de réponse souhaité : JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            plan = self._parse_fertilization_plan(response.text)
            return plan
        except Exception as e:
            print(f"Erreur lors de la génération du plan de fertilisation: {str(e)}")
            return self._get_default_fertilization_plan()
    
    def _parse_management_plan(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire le plan de gestion"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Structure le plan à partir du texte
            plan = {
                "timestamp": datetime.now().isoformat(),
                "planting": {},
                "irrigation": {},
                "fertilization": {},
                "pest_control": {},
                "cultural_practices": [],
                "labor_equipment": {},
                "yield_estimate": None
            }
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "densité" in line.lower() or "espacement" in line.lower():
                    plan["planting"]["density"] = line
                elif "irrigation" in line.lower():
                    if "fréquence" in line.lower():
                        plan["irrigation"]["frequency"] = line
                    elif "méthode" in line.lower():
                        plan["irrigation"]["method"] = line
                elif "fertilisation" in line.lower():
                    if "dose" in line.lower():
                        plan["fertilization"]["dosage"] = line
                    elif "période" in line.lower():
                        plan["fertilization"]["timing"] = line
                
                if line.endswith(":"):
                    current_section = line[:-1].lower()
                elif current_section:
                    if "pratique" in current_section:
                        plan["cultural_practices"].append(line)
                    elif "rendement" in current_section:
                        plan["yield_estimate"] = self._extract_numeric_value(line)
            
            return plan
    
    def _parse_irrigation_schedule(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire le calendrier d'irrigation"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "timestamp": datetime.now().isoformat(),
                "daily_water_needs": None,
                "irrigation_frequency": None,
                "session_duration": None,
                "recommended_methods": [],
                "growth_stage_adjustments": [],
                "monitoring_indicators": [],
                "water_saving_measures": []
            }
    
    def _parse_fertilization_plan(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire le plan de fertilisation"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "timestamp": datetime.now().isoformat(),
                "recommended_fertilizers": [],
                "application_doses": {},
                "application_schedule": [],
                "application_methods": [],
                "stage_adjustments": [],
                "monitoring_plan": [],
                "sustainable_practices": []
            }
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extrait une valeur numérique d'une chaîne de texte"""
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return float(numbers[0]) if numbers else None
    
    def _get_default_management_plan(self, crop_type: str, area: float) -> Dict[str, Any]:
        """Retourne un plan de gestion par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "crop_type": crop_type,
            "area": area,
            "planting": {
                "density": "À déterminer",
                "spacing": "À déterminer"
            },
            "irrigation": {
                "method": "À définir",
                "frequency": "À définir"
            },
            "fertilization": {
                "products": "À définir",
                "schedule": "À définir"
            },
            "pest_control": {
                "strategy": "À développer",
                "products": "À définir"
            },
            "cultural_practices": [
                "Pratiques à définir selon les conditions locales"
            ],
            "labor_equipment": {
                "labor_needs": "À évaluer",
                "equipment_needs": "À déterminer"
            },
            "yield_estimate": None
        }
    
    def _get_default_irrigation_schedule(self) -> Dict[str, Any]:
        """Retourne un calendrier d'irrigation par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "daily_water_needs": None,
            "irrigation_frequency": "À déterminer",
            "session_duration": "À définir",
            "recommended_methods": ["Méthodes à évaluer"],
            "growth_stage_adjustments": ["Ajustements à définir"],
            "monitoring_indicators": ["Indicateurs à suivre"],
            "water_saving_measures": ["Mesures à mettre en place"]
        }
    
    def _get_default_fertilization_plan(self) -> Dict[str, Any]:
        """Retourne un plan de fertilisation par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "recommended_fertilizers": ["À déterminer"],
            "application_doses": {},
            "application_schedule": ["Calendrier à définir"],
            "application_methods": ["Méthodes à évaluer"],
            "stage_adjustments": ["Ajustements à définir"],
            "monitoring_plan": ["Plan à développer"],
            "sustainable_practices": ["Pratiques à identifier"]
        }
