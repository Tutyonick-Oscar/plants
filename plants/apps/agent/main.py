from typing import Dict, Optional, Union, List
import json
import os
from dataclasses import dataclass
from plants.apps.agent.agents.planning_agent import PlanningAgent

DEFAULT_GEMINI_API_KEY = 'AIzaSyDhEN4OMZ-8K0MlNmMg7q9CT-dQ33iu9iE'
DEFAULT_WEATHER_API_KEY = '7d1746c60628ad534aa00ef0cf84e426'

@dataclass
class ProjectRequest:
    """Structure de la requête pour créer un projet agricole."""
    objective: str
    country: str
    location: str
    gemini_api_key: str = DEFAULT_GEMINI_API_KEY
    weather_api_key: str = DEFAULT_WEATHER_API_KEY

@dataclass
class ProjectResponse:
    """Structure de la réponse contenant l'analyse et le projet détaillé."""
    success: bool
    message: str
    analysis: Optional[Dict] = None
    project: Optional[Dict] = None

def create_agricultural_project(request_data: Union[Dict, ProjectRequest]) -> Dict:
    """Crée un projet agricole basé sur l'objectif, le pays et la localisation.
    
    Args:
        request_data: Peut être soit un dictionnaire avec les clés suivantes :
            {
                "objective": str - Objectif du projet (ex: "Je souhaite cultiver du maïs pour ma famille")
                "country": str - Pays du projet
                "location": str - Ville du projet
            }
            Ou une instance de ProjectRequest
    
    Returns:
        Dict avec la structure suivante :
        {
            "success": bool - True si la requête a réussi, False sinon
            "message": str - Message de succès ou d'erreur
            "analysis": {
                # Analyse initiale du projet
                "type_culture": str,
                "superficie": str,
                "duree": str,
                "budget": str,
                ...
            },
            "project": {
                # Détails complets du projet
                "preparation_terrain": {...},
                "approvisionnement": {...},
                ...
            }
        }
    """
    try:
        # Valider et extraire les données de la requête
        if isinstance(request_data, dict):
            # Vérifier les champs requis
            required_fields = ["objective", "country", "location"]
            missing_fields = [field for field in required_fields if field not in request_data]
            if missing_fields:
                raise ValueError(f"Champs manquants : {', '.join(missing_fields)}")
            
            # Créer la requête avec les valeurs par défaut pour les clés API
            request = ProjectRequest(
                objective=request_data["objective"],
                country=request_data["country"],
                location=request_data["location"],
                gemini_api_key=request_data.get("gemini_api_key", DEFAULT_GEMINI_API_KEY),
                weather_api_key=request_data.get("weather_api_key", DEFAULT_WEATHER_API_KEY)
            )
        elif isinstance(request_data, ProjectRequest):
            request = request_data
        else:
            raise ValueError("request_data doit être un dictionnaire ou une instance de ProjectRequest")
        
        # Initialiser l'agent
        planning_agent = PlanningAgent(
            api_key=request.gemini_api_key,
            weather_api_key=request.weather_api_key
        )
        
        # Générer l'analyse initiale
        analysis = planning_agent.generate_project_analysis(
            project_name="Projet Agricole",
            objective=request.objective,
            location=f"{request.location}, {request.country}"
        )
        
        if not analysis:
            return ProjectResponse(
                success=False,
                message="Échec de l'analyse initiale du projet",
                analysis=None,
                project=None
            ).__dict__
        
        # Générer le projet détaillé
        project = planning_agent.create_detailed_project(
            objective=request.objective,
            location=f"{request.location}, {request.country}", 
            analysis=analysis
        )
        
        if not project:
            return ProjectResponse(
                success=False,
                message="Échec de la création du projet détaillé",
                analysis=analysis,
                project=None
            ).__dict__
        
        # Retourner la réponse complète
        return ProjectResponse(
            success=True,
            message="Projet créé avec succès",
            analysis=analysis,
            project=project
        ).__dict__
    
    except ValueError as e:
        return ProjectResponse(
            success=False,
            message=f"Erreur de validation : {str(e)}",
            analysis=None,
            project=None
        ).__dict__
    except Exception as e:
        return ProjectResponse(
            success=False,
            message=f"Erreur inattendue : {str(e)}",
            analysis=None,
            project=None
        ).__dict__

if __name__ == "__main__":
   
    # Test avec un pays non supporté
    request_invalid_country = {
        "objective": "Je souhaite cultiver du maïs pour ma famille",
        "country": "Uganda",
        "location": "Kampala"
    }
    result_invalid_country = create_agricultural_project(request_invalid_country)
    print("\nTest avec un pays non supporté:")
    print(json.dumps(result_invalid_country, indent=2, ensure_ascii=False))
