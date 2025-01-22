from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from pydantic import BaseModel, Field
import json
from datetime import datetime
import logging
import time
from tavily import TavilyClient
import os
import hashlib
import pickle
from pathlib import Path
from ratelimit import limits, sleep_and_retry
import functools
import signal
from google.api_core import exceptions as google_exceptions
from typing import Any

# load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Définition des constantes
MAX_RETRIES = 3
INITIAL_WAIT = 5  # Augmenté à 5 secondes
MAX_WAIT = 60  # Augmenté à 60 secondes
CACHE_DIR = Path("cache")
CACHE_DURATION = 3600  # 1 heure en secondes
CALLS_PER_MINUTE = 5  # Réduit à 5 appels par minute
API_TIMEOUT = 15  # Augmenté à 15 secondes

# Créer le dossier cache s'il n'existe pas
CACHE_DIR.mkdir(exist_ok=True)

class TimeoutError(Exception):
    """Erreur levée quand une opération dépasse le timeout"""
    pass

def timeout_handler(signum, frame):
    """Gestionnaire pour le signal de timeout"""
    raise TimeoutError("L'opération a dépassé le délai d'attente")

def with_timeout(seconds):
    """Décorateur pour ajouter un timeout à une fonction"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Configurer le gestionnaire de signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Désactiver l'alarme
                signal.alarm(0)
            return result
        return wrapper
    return decorator

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=60)
@with_timeout(API_TIMEOUT)
def rate_limited_api_call(model, prompt: str) -> str:
    """Effectue un appel API avec limitation de débit et timeout"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except google_exceptions.ResourceExhausted:
        logger.error(f"Quota API dépassé, délai d'attente de {INITIAL_WAIT} secondes")
        time.sleep(INITIAL_WAIT)
        raise
    except TimeoutError:
        logger.error(f"Timeout après {API_TIMEOUT} secondes")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'appel API: {str(e)}")
        raise

class ResearchResult(BaseModel):
    """Modèle pour les résultats de recherche"""
    title: str
    url: str
    summary: str
    relevance_score: float
    source_type: str
    date_published: Optional[str]
    content: Optional[str] = None

class ResearchAgent(BaseModel):
    """Agent de recherche pour les informations agricoles"""
    
    api_key: str
    model: Optional[Any] = None
    last_api_call: float = 0.0
    
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def search_agricultural_data(self, query: str, max_results: int = 5) -> List[ResearchResult]:
        """Recherche des informations agricoles pertinentes"""
        try:
            prompt = f"""En tant qu'expert en agriculture, recherchez des informations pertinentes sur : {query}
            
            Fournissez une analyse détaillée incluant :
            1. Meilleures pratiques
            2. Conditions optimales
            3. Défis courants
            4. Solutions recommandées
            5. Innovations récentes
            
            Format de réponse souhaité : JSON
            """
            
            response = self._generate_content_with_retry(prompt)
            return self._parse_research_results(response, max_results)
        except Exception as e:
            logger.error(f"Erreur lors de la recherche : {str(e)}")
            return []
    
    def analyze_crop_data(self, crop_name: str, region: str) -> Dict:
        """Analyse approfondie d'une culture spécifique"""
        try:
            prompt = f"""En tant qu'expert en agronomie, analysez la culture de {crop_name} dans la région de {region}.
            
            Fournissez une analyse détaillée incluant :
            1. Conditions de croissance optimales
            2. Calendrier cultural
            3. Besoins en nutriments
            4. Maladies et ravageurs communs
            5. Rendements attendus
            
            Format de réponse souhaité : JSON
            """
            
            response = self._generate_content_with_retry(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse : {str(e)}")
            return self._get_default_crop_analysis()
    
    def get_market_insights(self, crop_name: str) -> Dict:
        """Obtient des informations sur le marché d'une culture"""
        try:
            prompt = f"""En tant qu'expert en marchés agricoles, analysez le marché de {crop_name}.
            
            Fournissez une analyse détaillée incluant :
            1. Tendances actuelles des prix
            2. Prévisions de marché
            3. Principaux acheteurs
            4. Opportunités de commercialisation
            5. Risques potentiels
            
            Format de réponse souhaité : JSON
            """
            
            response = self._generate_content_with_retry(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de marché : {str(e)}")
            return self._get_default_market_insights()
    
    def _generate_content_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Génère du contenu avec retry en cas d'erreur"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1 * (attempt + 1))
    
    def _parse_research_results(self, response: str, max_results: int) -> List[ResearchResult]:
        """Parse les résultats de recherche"""
        try:
            data = json.loads(response)
            results = []
            for item in data[:max_results]:
                result = ResearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    summary=item.get("summary", ""),
                    relevance_score=item.get("relevance_score", 0.0),
                    source_type=item.get("source_type", "unknown"),
                    date_published=item.get("date_published")
                )
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Erreur lors du parsing des résultats : {str(e)}")
            return []
    
    def _get_default_crop_analysis(self) -> Dict:
        """Retourne une analyse par défaut pour une culture"""
        return {
            "timestamp": datetime.now().isoformat(),
            "growing_conditions": {
                "temperature": "À déterminer",
                "soil_type": "À déterminer",
                "water_needs": "À déterminer"
            },
            "calendar": [],
            "nutrient_requirements": {},
            "pests_diseases": [],
            "expected_yield": None
        }
    
    def _get_default_market_insights(self) -> Dict:
        """Retourne des insights de marché par défaut"""
        return {
            "timestamp": datetime.now().isoformat(),
            "price_trends": [],
            "market_forecast": [],
            "buyers": [],
            "marketing_opportunities": [],
            "risks": []
        }

def get_fallback_response(query_type: str = "market") -> Dict:
    """Génère une réponse de fallback structurée selon le type de requête"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    if query_type == "market":
        return {
            "status": "limited",
            "message": "Service temporairement indisponible - Utilisation des données de secours",
            "source": "fallback_system",
            "generated_date": current_date,
            "market_data": {
                "status": "indisponible",
                "message": "Les données de marché ne sont pas accessibles actuellement",
                "alternatives": [
                    "Consultez les prix sur les marchés locaux",
                    "Contactez les coopératives agricoles de votre région",
                    "Vérifiez les bulletins agricoles récents"
                ]
            }
        }
    else:  # crop analysis
        return {
            "status": "limited",
            "message": "Service temporairement indisponible - Utilisation des données de secours",
            "source": "fallback_system",
            "generated_date": current_date,
            "crop_data": {
                "status": "indisponible",
                "message": "Les données détaillées ne sont pas accessibles actuellement",
                "general_recommendations": [
                    "Suivez les pratiques agricoles standard pour votre région",
                    "Consultez les services agricoles locaux",
                    "Surveillez les conditions météorologiques"
                ]
            }
        }
