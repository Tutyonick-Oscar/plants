from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re
from plants.apps.agent.agents.base_agent import BaseAgent
import google.generativeai as genai

class MarketAnalysisService(BaseAgent):
    """Service d'analyse de marché utilisant l'IA pour générer des insights"""
    
    def __init__(self, api_key: str):
        """Initialise le service avec la clé API"""
        super().__init__(api_key)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def get_market_data(self, crop_type: str, region: str) -> Dict[str, Any]:
        """Génère une analyse de marché pour une culture spécifique dans une région donnée"""
        
        prompt = f"""En tant qu'expert en analyse des marchés agricoles, générez une analyse détaillée au format JSON pour la culture de {crop_type} 
        dans la région de {region}.

        Le format JSON doit suivre exactement cette structure :
        {{
            "prix_actuel": "prix moyen actuel par kg",
            "tendance_prix": "tendance sur les 6 derniers mois",
            "demande": {{
                "locale": "niveau de demande locale",
                "export": "potentiel d'exportation",
                "tendance": "évolution prévue"
            }},
            "concurrence": {{
                "producteurs_locaux": "nombre estimé",
                "importations": "volume d'importations",
                "parts_marche": "répartition en pourcentage"
            }},
            "canaux_distribution": ["liste des canaux disponibles"],
            "opportunites": ["opportunités identifiées"],
            "risques_marche": ["risques potentiels"],
            "recommandations": ["recommandations stratégiques"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis = self.parse_json_response(response.text)
            return analysis
        except Exception as e:
            print(f"Erreur lors de l'analyse du marché: {str(e)}")
            return self._get_default_market_data(crop_type, region)
    
    def analyze_price_trends(self, crop_type: str, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les tendances de prix et génère des prévisions"""
        
        prompt = f"""En tant qu'analyste des marchés agricoles, analysez les tendances de prix suivantes pour {crop_type} et générez des prévisions.

Données historiques :
{json.dumps(historical_data, indent=2)}

Fournissez :
1. Analyse des tendances actuelles
2. Facteurs influençant les variations
3. Prévisions à court terme (3 mois)
4. Prévisions à moyen terme (6 mois)
5. Recommandations de timing pour la vente
6. Stratégies de gestion des risques de prix

Format de réponse souhaité : JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis = self._parse_price_analysis(response.text)
            return analysis
        except Exception as e:
            print(f"Erreur lors de l'analyse des prix: {str(e)}")
            return self._get_default_price_analysis()
    
    def generate_marketing_strategy(self, crop_data: Dict[str, Any], market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Génère une stratégie de commercialisation basée sur les conditions actuelles"""
        
        prompt = f"""En tant que stratège en commercialisation agricole, générez une stratégie détaillée basée sur les données suivantes :

Données de la culture :
{json.dumps(crop_data, indent=2)}

Conditions du marché :
{json.dumps(market_conditions, indent=2)}

Fournissez une stratégie incluant :
1. Canaux de distribution recommandés
2. Stratégie de prix
3. Timing optimal de mise en marché
4. Options de stockage et conservation
5. Partenariats potentiels
6. Stratégies de différenciation
7. Plan d'action détaillé
8. Indicateurs de performance à suivre

Format de réponse souhaité : JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            strategy = self._parse_marketing_strategy(response.text)
            return strategy
        except Exception as e:
            print(f"Erreur lors de la génération de la stratégie: {str(e)}")
            return self._get_default_marketing_strategy()
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire l'analyse de marché"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    def _parse_price_analysis(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire l'analyse des prix"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "timestamp": datetime.now().isoformat(),
                "current_trends": [],
                "influencing_factors": [],
                "short_term_forecast": [],
                "medium_term_forecast": [],
                "selling_recommendations": [],
                "risk_management_strategies": []
            }
    
    def _parse_marketing_strategy(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA pour extraire la stratégie marketing"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "timestamp": datetime.now().isoformat(),
                "distribution_channels": [],
                "pricing_strategy": {},
                "timing_recommendations": [],
                "storage_options": [],
                "potential_partnerships": [],
                "differentiation_strategies": [],
                "action_plan": [],
                "kpis": []
            }
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extrait une valeur numérique d'une chaîne de texte"""
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return float(numbers[0]) if numbers else None
    
    def _get_default_market_data(self, crop_type: str, region: str) -> Dict[str, Any]:
        """Retourne une analyse de marché par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "crop_type": crop_type,
            "region": region,
            "prix_actuel": "À déterminer",
            "tendance_prix": "À déterminer",
            "demande": {
                "locale": "À déterminer",
                "export": "À déterminer",
                "tendance": "À déterminer"
            },
            "concurrence": {
                "producteurs_locaux": "À déterminer",
                "importations": "À déterminer",
                "parts_marche": "À déterminer"
            },
            "canaux_distribution": [],
            "opportunites": [],
            "risques_marche": [],
            "recommandations": []
        }
    
    def _get_default_price_analysis(self) -> Dict[str, Any]:
        """Retourne une analyse des prix par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "current_trends": ["Données non disponibles"],
            "influencing_factors": ["Facteurs non identifiés"],
            "short_term_forecast": ["Prévisions non disponibles"],
            "medium_term_forecast": ["Prévisions non disponibles"],
            "selling_recommendations": ["Consultez les acteurs du marché"],
            "risk_management_strategies": ["Stratégies à développer"]
        }
    
    def _get_default_marketing_strategy(self) -> Dict[str, Any]:
        """Retourne une stratégie marketing par défaut en cas d'erreur"""
        return {
            "timestamp": datetime.now().isoformat(),
            "distribution_channels": ["À identifier"],
            "pricing_strategy": {
                "approach": "À définir",
                "factors": ["À déterminer"]
            },
            "timing_recommendations": ["À déterminer"],
            "storage_options": ["Options à évaluer"],
            "potential_partnerships": ["Partenaires à identifier"],
            "differentiation_strategies": ["Stratégies à développer"],
            "action_plan": ["Plan à élaborer"],
            "kpis": ["Indicateurs à définir"]
        }
