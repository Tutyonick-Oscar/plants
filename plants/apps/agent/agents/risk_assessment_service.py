from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re
from plants.apps.agent.agents.base_agent import BaseAgent
import google.generativeai as genai

class RiskAssessmentService(BaseAgent):
    """Service d'évaluation des risques utilisant l'IA pour générer des analyses de risques"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_risks(self, crop_type: str, location: str, weather_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyse les risques pour une culture spécifique.
        
        Args:
            crop_type: Type de culture
            location: Localisation du projet
            weather_data: Données météorologiques (optionnel)
            
        Returns:
            Dict contenant l'analyse des risques
        """
        weather_info = "Données météo non disponibles" if weather_data is None else str(weather_data)
        
        prompt = f"""En tant qu'expert en gestion des risques agricoles, générez une analyse détaillée au format JSON pour la culture de {crop_type} 
        dans la localisation {location}, en tenant compte des informations météo suivantes : {weather_info}.

        Le format JSON doit suivre exactement cette structure :
        {{
            "risques_climatiques": [
                {{
                    "type": "type de risque",
                    "probabilite": "probabilité en %",
                    "impact": "niveau d'impact",
                    "mesures_prevention": ["mesures à prendre"]
                }}
            ],
            "risques_biologiques": [
                {{
                    "type": "type de risque",
                    "probabilite": "probabilité en %",
                    "impact": "niveau d'impact",
                    "mesures_prevention": ["mesures à prendre"]
                }}
            ],
            "risques_economiques": [
                {{
                    "type": "type de risque",
                    "probabilite": "probabilité en %",
                    "impact": "niveau d'impact",
                    "mesures_prevention": ["mesures à prendre"]
                }}
            ],
            "risques_operationnels": [
                {{
                    "type": "type de risque",
                    "probabilite": "probabilité en %",
                    "impact": "niveau d'impact",
                    "mesures_prevention": ["mesures à prendre"]
                }}
            ],
            "niveau_risque_global": "niveau de risque global",
            "recommandations_prioritaires": ["recommandations prioritaires"],
            "plan_contingence": ["actions de contingence recommandées"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis = self._parse_risk_analysis(response.text)
            return analysis
        except Exception as e:
            print(f"Erreur lors de l'analyse des risques: {str(e)}")
            return self._get_default_risk_analysis(crop_type, location)
    
    def evaluate_disease_risks(self, crop_data: Dict[str, Any], weather_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue les risques spécifiques de maladies"""
        
        prompt = f"""En tant que phytopathologiste, évaluez les risques de maladies pour cette culture basés sur les données suivantes :

Données de la culture :
{json.dumps(crop_data, indent=2)}

Conditions météorologiques :
{json.dumps(weather_conditions, indent=2)}

Fournissez :
1. Maladies potentielles
2. Niveau de risque pour chaque maladie
3. Conditions favorables au développement
4. Symptômes à surveiller
5. Mesures préventives
6. Traitements recommandés
7. Stratégie de surveillance

Format de réponse souhaité : JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            evaluation = self._parse_disease_evaluation(response.text)
            return evaluation
        except Exception as e:
            print(f"Erreur lors de l'évaluation des maladies: {str(e)}")
            return self._get_default_disease_evaluation()
    
    def generate_mitigation_plan(self, identified_risks: Dict[str, Any], resources: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un plan d'atténuation des risques"""
        
        prompt = f"""En tant qu'expert en gestion des risques, générez un plan d'atténuation détaillé basé sur :

Risques identifiés :
{json.dumps(identified_risks, indent=2)}

Ressources disponibles :
{json.dumps(resources, indent=2)}

Fournissez un plan incluant :
1. Actions prioritaires
2. Mesures préventives
3. Protocoles d'intervention
4. Ressources nécessaires
5. Calendrier de mise en œuvre
6. Indicateurs de suivi
7. Plan de communication
8. Budget estimatif

Format de réponse souhaité : JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            plan = self._parse_mitigation_plan(response.text)
            return plan
        except Exception as e:
            print(f"Erreur lors de la génération du plan: {str(e)}")
            return self._get_default_mitigation_plan()
    
    def _parse_risk_analysis(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire l'analyse des risques"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Structure l'analyse à partir du texte
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "climate_risks": [],
                "pest_disease_risks": [],
                "agronomic_risks": [],
                "economic_risks": [],
                "prevention_measures": [],
                "contingency_plan": [],
                "potential_impact": {},
                "priority_recommendations": []
            }
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.endswith(":"):
                    current_section = line[:-1].lower()
                elif current_section:
                    if "climat" in current_section:
                        analysis["climate_risks"].append(line)
                    elif "maladie" in current_section or "ravageur" in current_section:
                        analysis["pest_disease_risks"].append(line)
                    elif "agronom" in current_section:
                        analysis["agronomic_risks"].append(line)
                    elif "économ" in current_section:
                        analysis["economic_risks"].append(line)
                    elif "prévention" in current_section:
                        analysis["prevention_measures"].append(line)
                    elif "contingence" in current_section:
                        analysis["contingency_plan"].append(line)
                    elif "impact" in current_section:
                        if "financier" in line.lower():
                            analysis["potential_impact"]["financial"] = self._extract_numeric_value(line)
                        elif "rendement" in line.lower():
                            analysis["potential_impact"]["yield"] = self._extract_numeric_value(line)
                    elif "recommand" in current_section:
                        analysis["priority_recommendations"].append(line)
            
            return analysis
    
    def _parse_disease_evaluation(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire l'évaluation des maladies"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "timestamp": datetime.now().isoformat(),
                "potential_diseases": [],
                "risk_levels": {},
                "favorable_conditions": [],
                "symptoms_to_monitor": [],
                "preventive_measures": [],
                "recommended_treatments": [],
                "monitoring_strategy": []
            }
    
    def _parse_mitigation_plan(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire le plan d'atténuation"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "timestamp": datetime.now().isoformat(),
                "priority_actions": [],
                "preventive_measures": [],
                "intervention_protocols": [],
                "required_resources": [],
                "implementation_timeline": [],
                "monitoring_indicators": [],
                "communication_plan": [],
                "estimated_budget": {}
            }
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extrait une valeur numérique d'une chaîne de texte"""
        import re
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return float(numbers[0]) if numbers else None
    
    def _get_default_risk_analysis(self, crop_type: str, location: str) -> Dict[str, Any]:
        """Retourne une analyse des risques par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "crop_type": crop_type,
            "location": location,
            "climate_risks": ["Risques à évaluer"],
            "pest_disease_risks": ["Risques à identifier"],
            "agronomic_risks": ["Risques à analyser"],
            "economic_risks": ["Risques à évaluer"],
            "prevention_measures": ["Mesures à définir"],
            "contingency_plan": ["Plan à développer"],
            "potential_impact": {
                "financial": None,
                "yield": None
            },
            "priority_recommendations": [
                "Une analyse détaillée des risques est recommandée",
                "Consultez les experts locaux"
            ]
        }
    
    def _get_default_disease_evaluation(self) -> Dict[str, Any]:
        """Retourne une évaluation des maladies par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "potential_diseases": ["À identifier"],
            "risk_levels": {},
            "favorable_conditions": ["À déterminer"],
            "symptoms_to_monitor": ["À définir"],
            "preventive_measures": ["À développer"],
            "recommended_treatments": ["À déterminer"],
            "monitoring_strategy": ["À élaborer"]
        }
    
    def _get_default_mitigation_plan(self) -> Dict[str, Any]:
        """Retourne un plan d'atténuation par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "priority_actions": ["À définir"],
            "preventive_measures": ["À développer"],
            "intervention_protocols": ["À établir"],
            "required_resources": ["À identifier"],
            "implementation_timeline": ["À planifier"],
            "monitoring_indicators": ["À définir"],
            "communication_plan": ["À élaborer"],
            "estimated_budget": {}
        }
