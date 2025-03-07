import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from plants.apps.agent.agents.base_agent import BaseAgent
from plants.apps.agent.agents.crop_management_service import CropManagementService
from plants.apps.agent.agents.market_analysis_service import MarketAnalysisService
from plants.apps.agent.agents.research_agent import ResearchAgent
from plants.apps.agent.agents.risk_assessment_service import RiskAssessmentService
from plants.apps.agent.agents.soil_analysis_service import SoilAnalysisService
from plants.apps.agent.agents.weather_service import WeatherService

logger = logging.getLogger(__name__)


@dataclass
class Location:
    region: str
    latitude: float
    longitude: float


@dataclass
class Equipment:
    name: str
    type: str
    capacity: float
    status: str
    last_maintenance: datetime
    quantity: int = 1


@dataclass
class Field:
    name: str
    area: float
    location: Location
    soil_type: str
    current_crop: Optional[str] = None
    irrigation_system: Optional[str] = None
    soil_ph: Optional[float] = None
    organic_matter: Optional[float] = None


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Représente une tâche agricole."""

    title: str
    description: str
    priority: TaskPriority
    field_id: int
    id: Optional[int] = None
    status: TaskStatus = TaskStatus.PENDING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    dependencies: List[int] = field(default_factory=list)
    weather_constraints: Dict[str, float] = field(default_factory=dict)
    equipment_required: List[Equipment] = field(default_factory=list)
    estimated_duration: float = 0.0  # en heures

    def is_weather_suitable(self, weather_data: Dict) -> bool:
        """Vérifie si les conditions météo sont adaptées à la tâche."""
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        precipitation = weather_data.get("rain", {}).get("1h", 0)
        temperature = weather_data.get("main", {}).get("temp", 20)

        return (
            wind_speed <= self.weather_constraints.get("max_wind_speed", 30)
            and precipitation <= self.weather_constraints.get("max_precipitation", 5)
            and self.weather_constraints.get("min_temperature", 5)
            <= temperature
            <= self.weather_constraints.get("max_temperature", 35)
        )

    def calculate_cost(self) -> float:
        """Calcule le coût estimé de la tâche."""
        equipment_cost = sum(eq.capacity * eq.status for eq in self.equipment_required)
        return equipment_cost * (self.estimated_duration / 24.0)

    def to_json(self) -> Dict:
        """Convertit l'objet en dictionnaire JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "equipment_required": [eq.__dict__ for eq in self.equipment_required],
            "estimated_duration": self.estimated_duration,
            "priority": self.priority.value,
            "status": self.status.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "dependencies": self.dependencies,
            "field_id": self.field_id,
            "weather_constraints": self.weather_constraints,
        }


class TaskScheduler:
    """Gestionnaire de planification des tâches."""

    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> Task:
        """Ajoute une nouvelle tâche."""
        if task.id is None:
            task.id = len(self.tasks) + 1
        self.tasks.append(task)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Récupère une tâche par son ID."""
        return next((task for task in self.tasks if task.id == task_id), None)

    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """Met à jour le statut d'une tâche."""
        task = self.get_task(task_id)
        if task:
            task.status = status
            return True
        return False

    def get_dependent_tasks(self, task_id: int) -> List[Task]:
        """Récupère toutes les tâches qui dépendent de la tâche donnée."""
        return [task for task in self.tasks if task_id in task.dependencies]

    def schedule_tasks(self, weather_service: WeatherService) -> List[Dict]:
        """Planifie les tâches en fonction des contraintes."""
        scheduled_tasks = []
        pending_tasks = [t for t in self.tasks if t.status == TaskStatus.PENDING]

        # Trier par priorité et dépendances
        pending_tasks.sort(
            key=lambda x: (
                len(x.dependencies),
                {"low": 0, "medium": 1, "high": 2, "urgent": 3}[x.priority.value],
            )
        )

        current_date = datetime.now()

        for task in pending_tasks:
            # Vérifier les dépendances
            dependencies_met = all(
                self.get_task(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )

            if not dependencies_met:
                continue

            # Trouver le prochain créneau disponible
            while True:
                weather = weather_service.get_current_weather(
                    task.field_id, task.field_id
                )

                if task.is_weather_suitable(weather):
                    task.start_date = current_date
                    task.end_date = current_date + datetime.timedelta(
                        hours=task.estimated_duration
                    )
                    task.status = TaskStatus.PENDING
                    scheduled_tasks.append(task.to_json())
                    break

                current_date += datetime.timedelta(hours=1)

        return scheduled_tasks


class PlanningAgent(BaseAgent):
    """Agent responsable de la planification agricole."""

    def __init__(self, api_key: str, weather_api_key: str):
        """Initialise l'agent de planification.

        Args:
            api_key: Clé API pour le modèle Gemini
            weather_api_key: Clé API pour le service météo
        """
        super().__init__(api_key)
        self.weather_api_key = weather_api_key

        # Initialiser les services
        self.weather_service = WeatherService(self.weather_api_key)
        self.soil_analysis_service = SoilAnalysisService(self.api_key)
        self.market_analysis_service = MarketAnalysisService(self.api_key)
        self.crop_management_service = CropManagementService(self.api_key)
        self.risk_assessment_service = RiskAssessmentService(self.api_key)
        self.task_scheduler = TaskScheduler()
        self.research_agent = ResearchAgent(api_key=self.api_key)

    def analyze_field_requirements(self, field: Field) -> Dict:
        """Analyse les besoins du champ et recommande les équipements et ressources nécessaires."""
        # Obtenir les prévisions météo
        weather_analysis = self.weather_service.analyze_growing_conditions(
            field.location.latitude,
            field.location.longitude,
            field.current_crop or "maïs",
        )

        # Obtenir les données de recherche
        research_data = self.research_agent.analyze_crop_data(
            field.current_crop or "maïs", field.location.region
        )

        # Obtenir les besoins du sol
        soil_requirements = self.soil_service.get_soil_requirements(
            field.current_crop or "maïs"
        )

        prompt = f"""
En tant qu'expert agricole, analysez ce champ et fournissez des recommandations détaillées adaptées à la production optimale dans les conditions suivantes :

**Caractéristiques du champ :**
- Taille : {field.area} hectares
- Type de sol : {field.soil_type}
- Région : {field.location.region}
- Culture actuelle : {field.current_crop}
- Système d'irrigation : {field.irrigation_system}
- pH du sol : {field.soil_ph}
- Matière organique : {field.organic_matter}%
- Système d'irrigation : {field.irrigation_system}

**Analyse climatique :**
- Score global : {weather_analysis['score_global']} (sur 10)
- Risques immédiats : {', '.join(weather_analysis['risques_immediats'])}
- Conditions favorables : {', '.join(weather_analysis['conditions_favorables'])}

**Données de recherche :**
{json.dumps(research_data, indent=2)}

**Besoins du sol :**
{json.dumps(soil_requirements, indent=2)}

**Tâches demandées :**
1. **Équipements agricoles nécessaires** : Listez les équipements spécifiques (avec quantités) adaptés à la taille et au type de sol.
2. **Systèmes d'irrigation recommandés** : Indiquez les options optimales selon le type de sol, le système actuel et les conditions climatiques.
3. **Amendements du sol requis** : Fournissez une liste des engrais, amendements organiques ou chimiques nécessaires pour équilibrer le pH et améliorer la matière organique.
4. **Main d'œuvre estimée** : Décrivez le nombre d'ouvriers nécessaires pour chaque étape (préparation du sol, plantation, entretien, récolte) et les compétences spécifiques requises.
5. **Budget estimé** : Fournissez un budget clair et détaillé par poste (intrants, main-d'œuvre, matériel, irrigation, etc.).
6. **Calendrier des travaux** : Proposez un calendrier précis, étape par étape, basé sur les conditions climatiques et la culture actuelle.

**Directives :**
- Adaptez vos recommandations aux conditions climatiques et géographiques décrites.
- Soyez précis et pratique, en expliquant brièvement les raisons derrière chaque recommandation.
- Fournissez des conseils pour minimiser les risques et maximiser les rendements.

**Livrable attendu :**
Une réponse structurée et exploitable qui intègre tous les éléments mentionnés ci-dessus, adaptée à la production agricole optimale.
"""

        response = self.model.generate_content(prompt)
        analysis = self._parse_field_analysis(response.text)
        analysis["weather_analysis"] = weather_analysis
        analysis["research_data"] = research_data
        analysis["soil_requirements"] = soil_requirements
        return {
            "recommendations": analysis.get("recommendations", []),
            "required_equipment": analysis.get("required_equipment", []),
            "estimated_costs": analysis.get("estimated_costs", {}),
            "risk_factors": analysis.get("risk_factors", []),
        }

    def create_crop_plan(self, field: Field, target_crop: str, budget: float) -> Dict:
        """Crée un plan détaillé de culture basé sur les caractéristiques du champ."""
        # Obtenir les prévisions météo
        weather_analysis = self.weather_service.analyze_growing_conditions(
            field.location.latitude, field.location.longitude, target_crop
        )

        # Obtenir les données de recherche et de marché
        research_data = self.research_agent.analyze_crop_data(
            target_crop, field.location.region
        )
        market_data = self.market_service.get_market_data(
            target_crop, field.location.region
        )

        prompt = f"""Créez un plan détaillé de culture pour:
        Culture cible: {target_crop}
        Taille du champ: {field.area} hectares
        Budget disponible: {budget} €
        Type de sol: {field.soil_type}
        Région: {field.location.region}

        Conditions météorologiques:
        Score global: {weather_analysis['score_global']}
        Risques immédiats: {', '.join(weather_analysis['risques_immediats'])}
        Conditions favorables: {', '.join(weather_analysis['conditions_favorables'])}
        Recommandations météo: {', '.join(weather_analysis['recommandations'])}

        Données de recherche:
        {json.dumps(research_data, indent=2)}

        Données de marché:
        {json.dumps(market_data, indent=2)}

        Le plan doit inclure:
        1. Variété recommandée et justification
        2. Calendrier précis (préparation, semis, entretien, récolte)
        3. Liste d'équipements avec périodes d'utilisation
        4. Estimation du rendement avec justification
        5. Analyse des risques et mesures de mitigation
        6. Budget détaillé
        7. Besoins en main d'œuvre
        8. Recommandations pour l'irrigation

        Adaptez le plan en fonction des conditions météorologiques prévues, des données de recherche et du marché.
        """

        response = self.model.generate_content(prompt)
        plan = self._parse_crop_plan(response.text)
        return plan

    def optimize_equipment_usage(
        self, field: Field, equipment: List[Equipment], current_conditions: Dict
    ) -> Dict:
        """
        Optimise l'utilisation des équipements agricoles en fonction des conditions actuelles.

        Args:
            field: Informations sur le champ
            equipment: Liste des équipements disponibles
            current_conditions: Conditions actuelles (météo, sol, etc.)

        Returns:
            Dict contenant les recommandations d'utilisation optimisée
        """
        # Obtenir les données météo actuelles
        weather = self.weather_service.get_current_weather(
            field.location.latitude, field.location.longitude
        )

        # Obtenir les recommandations de recherche
        research_data = self.research_agent.get_crop_recommendations(
            field.current_crop, field.location.region
        )

        # Obtenir les besoins du sol
        soil_requirements = self.soil_service.get_soil_requirements(field.current_crop)

        # Construire le prompt pour l'analyse
        prompt = f"""
En tant qu'expert en optimisation d'équipements agricoles, analysez la situation suivante et fournissez des recommandations détaillées :

DONNÉES DU CHAMP :
- Taille : {field.area} hectares
- Type de sol : {field.soil_type}
- Culture : {field.current_crop}
- pH du sol : {field.soil_ph}
- Matière organique : {field.organic_matter}%
- Système d'irrigation : {field.irrigation_system}

CONDITIONS ACTUELLES :
- Température : {weather.get('main', {}).get('temp', 'N/A')}°C
- Humidité : {weather.get('main', {}).get('humidity', 'N/A')}%
- Vent : {weather.get('wind', {}).get('speed', 'N/A')} km/h
- Précipitations : {weather.get('rain', {}).get('1h', 0)} mm/h

ÉQUIPEMENTS DISPONIBLES :
{json.dumps([e.__dict__ for e in equipment], indent=2)}

DONNÉES DE RECHERCHE :
{json.dumps(research_data, indent=2)}

BESOINS DU SOL :
{json.dumps(soil_requirements, indent=2)}

Fournissez des recommandations détaillées pour :
1. PLANIFICATION :
   - Planning optimal d'utilisation de chaque équipement
   - Séquence des opérations
   - Périodes optimales d'intervention

2. OPTIMISATION :
   - Réglages spécifiques pour chaque équipement
   - Vitesse de travail recommandée
   - Profondeur de travail si applicable
   - Paramètres d'application pour les produits

3. MAINTENANCE :
   - Vérifications prioritaires avant utilisation
   - Points d'attention particuliers
   - Maintenance préventive recommandée

4. ÉCONOMIES :
   - Suggestions pour réduire la consommation de carburant
   - Optimisation des trajets
   - Regroupement des opérations si possible

5. SÉCURITÉ :
   - Précautions spécifiques aux conditions
   - EPI recommandés
   - Zones ou conditions à éviter

Format de réponse attendu : JSON structuré avec recommandations détaillées pour chaque catégorie.
"""

        try:
            # Générer les recommandations
            response = self.model.generate_content(prompt)
            recommendations = json.loads(response.text)

            # Valider et structurer les recommandations
            return {
                "recommendations": recommendations.get("recommendations", []),
                "settings": recommendations.get("settings", {}),
                "schedule": recommendations.get("schedule", []),
                "efficiency_gains": recommendations.get("efficiency_gains", {}),
                "cost_savings": recommendations.get("cost_savings", {}),
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation des équipements: {str(e)}")
            return {
                "recommendations": [],
                "settings": {},
                "schedule": [],
                "efficiency_gains": {},
                "cost_savings": {},
            }

    def create_task(
        self,
        title: str,
        description: str,
        equipment: List[Equipment],
        duration: float,
        priority: TaskPriority,
        field: Field,
        dependencies: List[int] = [],
        weather_constraints: Optional[Dict[str, float]] = None,
    ) -> Task:
        """Crée une nouvelle tâche agricole"""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            field_id=field.name,
            equipment_required=equipment,
            estimated_duration=duration,
            dependencies=dependencies,
            weather_constraints=weather_constraints or {},
        )
        return self.task_scheduler.add_task(task)

    def generate_tasks_for_field(
        self, field: Field, equipment: List[Equipment]
    ) -> List[Dict]:
        """Génère automatiquement les tâches nécessaires pour un champ"""
        prompt = f"""
Générez une liste de tâches agricoles au format JSON suivant :
{{
    "tasks": [
        {{
            "title": "string",
            "description": "string",
            "equipment_required": ["string"],
            "duration": number,
            "priority": "high|medium|low",
            "weather_constraints": {{
                "max_wind_speed": number,
                "max_precipitation": number,
                "min_temperature": number,
                "max_temperature": number
            }},
            "dependencies": [number]
        }}
    ]
}}

Champ : {field.area}ha, {field.soil_type}, {field.current_crop}
Équipements : {", ".join(eq.name for eq in equipment)}
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Nettoyer la réponse
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            response_text = response_text.strip()

            logger.info(f"Réponse reçue : {response_text}")
            tasks_data = json.loads(response_text)

            created_tasks = []
            for task_data in tasks_data["tasks"]:
                required_equipment = [
                    eq
                    for eq in equipment
                    if eq.name in task_data.get("equipment_required", [])
                ]

                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    priority=TaskPriority(task_data["priority"].lower()),
                    field_id=field.name,
                    equipment_required=required_equipment,
                    estimated_duration=float(task_data["duration"]),
                    dependencies=task_data.get("dependencies", []),
                    weather_constraints=task_data.get("weather_constraints", {}),
                )
                created_tasks.append(task.to_json())

            return created_tasks

        except json.JSONDecodeError as e:
            logger.error(
                f"Erreur de parsing JSON : {str(e)}\nRéponse : {response_text}"
            )
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la génération des tâches : {str(e)}")
            return []

    def generate_objective_plan(self, field: Field, objective: Dict) -> Dict:
        """
        Génère un plan détaillé et professionnel pour un projet agricole, incluant des conseils d'expert.

        Args:
            field: Informations sur le champ
            objective: Dictionnaire contenant les détails de l'objectif

        Returns:
            Dict contenant le plan détaillé avec les tâches et ressources
        """
        try:
            json_structure = """{
    "project_overview": {
        "title": "",
        "description": "",
        "objectives": [],
        "expected_outcomes": []
    },
    "market_analysis": {
        "target_markets": [],
        "competition_analysis": [],
        "price_trends": [],
        "opportunities": [],
        "threats": []
    },
    "technical_analysis": {
        "soil_evaluation": {
            "current_state": [],
            "improvement_needs": [],
            "recommendations": []
        },
        "climate_analysis": {
            "seasonal_patterns": [],
            "risks": [],
            "mitigation_strategies": []
        },
        "water_management": {
            "requirements": [],
            "sources": [],
            "irrigation_plan": []
        }
    },
    "implementation_plan": {
        "preparation_phase": {
            "tasks": [],
            "duration": "",
            "key_milestones": [],
            "expert_advice": []
        },
        "development_phase": {
            "tasks": [],
            "duration": "",
            "key_milestones": [],
            "expert_advice": []
        },
        "operational_phase": {
            "tasks": [],
            "duration": "",
            "key_milestones": [],
            "expert_advice": []
        }
    },
    "resource_planning": {
        "equipment": {
            "required_items": [],
            "specifications": {},
            "estimated_costs": {},
            "procurement_advice": []
        },
        "infrastructure": {
            "required_items": [],
            "specifications": {},
            "estimated_costs": {},
            "construction_advice": []
        },
        "human_resources": {
            "roles": [],
            "skills_required": [],
            "training_needs": [],
            "management_advice": []
        }
    },
    "operational_guidelines": {
        "daily_operations": {
            "morning_tasks": [],
            "afternoon_tasks": [],
            "evening_tasks": [],
            "monitoring_points": []
        },
        "weekly_operations": {
            "maintenance_tasks": [],
            "monitoring_tasks": [],
            "planning_tasks": []
        },
        "monthly_operations": {
            "major_tasks": [],
            "evaluations": [],
            "adjustments": []
        },
        "seasonal_operations": {
            "pre_season": [],
            "during_season": [],
            "post_season": []
        }
    },
    "financial_projections": {
        "initial_investment": {
            "breakdown": {},
            "funding_options": [],
            "expert_advice": []
        },
        "operational_costs": {
            "fixed_costs": {},
            "variable_costs": {},
            "optimization_suggestions": []
        },
        "revenue_projections": {
            "scenarios": {
                "conservative": {},
                "realistic": {},
                "optimistic": {}
            },
            "key_assumptions": []
        },
        "profitability_analysis": {
            "break_even_analysis": {},
            "roi_projection": {},
            "cash_flow_forecast": {}
        }
    },
    "risk_management": {
        "agricultural_risks": {
            "identified_risks": [],
            "prevention_measures": [],
            "contingency_plans": []
        },
        "market_risks": {
            "identified_risks": [],
            "prevention_measures": [],
            "contingency_plans": []
        },
        "financial_risks": {
            "identified_risks": [],
            "prevention_measures": [],
            "contingency_plans": []
        }
    },
    "monitoring_and_evaluation": {
        "key_performance_indicators": {
            "production_kpis": [],
            "financial_kpis": [],
            "sustainability_kpis": []
        },
        "monitoring_schedule": {
            "daily_checks": [],
            "weekly_reviews": [],
            "monthly_assessments": []
        },
        "evaluation_methods": {
            "data_collection": [],
            "analysis_procedures": [],
            "reporting_templates": []
        }
    },
    "sustainability_plan": {
        "environmental_measures": {
            "conservation_practices": [],
            "resource_efficiency": [],
            "biodiversity_protection": []
        },
        "social_impact": {
            "community_benefits": [],
            "employment_creation": [],
            "knowledge_transfer": []
        },
        "long_term_sustainability": {
            "soil_health_practices": [],
            "water_conservation": [],
            "ecosystem_preservation": []
        }
    },
    "expert_recommendations": {
        "critical_success_factors": [],
        "potential_pitfalls": [],
        "best_practices": [],
        "innovation_opportunities": [],
        "scaling_strategies": []
    }
}"""

            prompt = f"""En tant qu'expert consultant en agronomie et gestion de projets agricoles, créez un plan professionnel détaillé pour le projet suivant:

CONTEXTE DU PROJET:
Type de projet: {objective['type']}
Description: {objective['description']}
Horizon temporel: {objective['timeline']}
Budget disponible: {objective['budget']} €

CARACTÉRISTIQUES TECHNIQUES:
- Surface: {field.area} hectares
- Type de sol: {field.soil_type}
- Culture actuelle: {field.current_crop}
- Système d'irrigation: {field.irrigation_system}
- pH du sol: {field.soil_ph}
- Matière organique: {field.organic_matter}%

Ressources existantes: {', '.join(objective['existing_resources'])}
Contraintes spécifiques: {', '.join(objective.get('constraints', []))}

DIRECTIVES:
1. Analysez en profondeur la faisabilité et la viabilité du projet
2. Fournissez des conseils d'expert détaillés pour chaque aspect
3. Proposez des solutions innovantes et durables
4. Incluez des recommandations pratiques et réalistes
5. Détaillez les étapes de mise en œuvre
6. Identifiez les facteurs clés de succès
7. Anticipez les défis potentiels et proposez des solutions
8. Intégrez les meilleures pratiques du secteur
9. Considérez les aspects environnementaux et sociaux
10. Fournissez un calendrier détaillé des opérations

Répondez avec un JSON complet et détaillé suivant exactement cette structure:
{json_structure}"""

            # Obtenir la réponse de l'IA
            response = self.model.generate_content(prompt)

            try:
                # Parser la réponse JSON
                plan = json.loads(response.text)
            except json.JSONDecodeError:
                # Si le parsing échoue, essayer de nettoyer la réponse
                clean_response = response.text.strip()
                start = clean_response.find("{")
                end = clean_response.rfind("}") + 1
                if start != -1 and end != 0:
                    clean_response = clean_response[start:end]
                plan = json.loads(clean_response)

            return plan

        except Exception as e:
            logger.error(f"Erreur lors de la génération du plan: {str(e)}")
            raise e

    def _can_operate_equipment(self, equipment: Equipment, weather: Dict) -> bool:
        """Détermine si un équipement peut être utilisé dans les conditions actuelles"""
        # Conditions météo défavorables
        if weather.get("rain", {}).get("1h", 0) > 5:  # Forte pluie
            return False
        if weather.get("wind", {}).get("speed", 0) > 30:  # Vent fort
            return False
        if equipment.type == "sprayer" and weather.get("wind", {}).get("speed", 0) > 15:
            return False  # Vent trop fort pour la pulvérisation
        return True

    def _get_optimal_settings(
        self, equipment: Equipment, field: Field, weather: Dict
    ) -> Dict:
        """Calcule les réglages optimaux pour un équipement"""
        settings = {"speed_kmh": 0, "depth_cm": 0, "width_m": equipment.capacity}

        # Ajuster la vitesse selon le type d'équipement et les conditions
        if equipment.type == "tractor":
            settings["speed_kmh"] = 8 if field.soil_type == "heavy" else 12
        elif equipment.type == "sprayer":
            settings["speed_kmh"] = (
                6 if weather.get("wind", {}).get("speed", 0) > 10 else 8
            )
        elif equipment.type == "harvester":
            settings["speed_kmh"] = 5 if field.soil_type == "wet" else 7

        # Ajuster la profondeur selon le type d'équipement et le sol
        if equipment.type in ["plow", "cultivator"]:
            settings["depth_cm"] = 15 if field.soil_type == "light" else 20

        return settings

    def calculate_roi(self, crop_plan: Dict, market_prices: Dict[str, float]) -> Dict:
        """Calcule le retour sur investissement estimé"""
        total_cost = crop_plan.get("estimated_cost", 0)
        estimated_revenue = crop_plan.get("estimated_yield", 0) * market_prices.get(
            crop_plan.get("crop_name", ""), 0
        )
        roi = (estimated_revenue - total_cost) / total_cost * 100

        return {
            "total_cost": total_cost,
            "estimated_revenue": estimated_revenue,
            "roi_percentage": roi,
            "break_even_point": total_cost
            / market_prices.get(crop_plan.get("crop_name", ""), 1),
            "risk_level": self._assess_risk_level(crop_plan.get("risk_factors", [])),
        }

    def _parse_field_analysis(self, response: str) -> Dict:
        """Parse la réponse de l'AI pour l'analyse du champ"""
        try:
            sections = response.split("\n\n")
            analysis = {
                "equipements": [],
                "irrigation": {},
                "amendements": [],
                "main_oeuvre": {},
                "budget": {},
                "calendrier": [],
            }

            current_section = None
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if "Équipements agricoles" in line:
                    current_section = "equipements"
                elif "Systèmes d'irrigation" in line:
                    current_section = "irrigation"
                elif "Amendements du sol" in line:
                    current_section = "amendements"
                elif "Main d'œuvre" in line:
                    current_section = "main_oeuvre"
                elif "Budget" in line:
                    current_section = "budget"
                elif "Calendrier" in line:
                    current_section = "calendrier"
                elif line and current_section:
                    if current_section in ["equipements", "amendements", "calendrier"]:
                        analysis[current_section].append(line)
                    else:
                        key = line.split(":")[0].strip() if ":" in line else line
                        value = line.split(":")[1].strip() if ":" in line else ""
                        analysis[current_section][key] = value

            return analysis
        except Exception as e:
            print(f"Erreur de parsing: {str(e)}")
            return {
                "equipements": ["Tracteur", "Semoir", "Système d'irrigation"],
                "irrigation": {"type": "Aspersion", "capacité": "10 hectares"},
                "amendements": ["Engrais NPK", "Chaux agricole"],
                "main_oeuvre": {"besoins": "3 personnes", "période": "6 mois"},
                "budget": {"estimation": "100000 €"},
                "calendrier": [
                    "Préparation: Mars",
                    "Semis: Avril",
                    "Récolte: Septembre",
                ],
            }

    def _calculate_harvest_date(self, planting_date: datetime) -> datetime:
        """Calcule la date de récolte en fonction de la date de plantation"""
        # Pour le maïs, on compte environ 5-6 mois de croissance
        months_to_add = 5
        new_month = ((planting_date.month - 1 + months_to_add) % 12) + 1
        new_year = planting_date.year + (
            (planting_date.month - 1 + months_to_add) // 12
        )
        return planting_date.replace(year=new_year, month=new_month)

    def _parse_crop_plan(self, response: str) -> Dict:
        """Parse la réponse de l'AI pour créer un plan de culture"""
        try:
            # Définir la date de plantation (par défaut en mai pour le maïs)
            current_date = datetime.now()
            planting_date = (
                current_date.replace(month=5)
                if current_date.month <= 5
                else current_date.replace(year=current_date.year + 1, month=5)
            )

            # Valeurs par défaut
            plan_data = {
                "crop_name": "maïs",
                "variety": "Hybride résistant",
                "planting_date": planting_date,
                "expected_harvest_date": self._calculate_harvest_date(planting_date),
                "required_equipment": [
                    "Tracteur",
                    "Charrue",
                    "Herse",
                    "Semoir",
                    "Système d'irrigation",
                    "Pulvérisateur",
                    "Moissonneuse",
                ],
                "estimated_yield": 8.5,  # tonnes/ha
                "estimated_cost": 100000.0,  # €
                "risk_factors": [
                    "Sécheresse",
                    "Maladies fongiques",
                    "Ravageurs (pyrales, sésamies)",
                    "Variations climatiques extrêmes",
                ],
            }

            # Parsing du texte de réponse
            for line in response.split("\n"):
                line = line.strip()
                if "Variété recommandée" in line and ":" in line:
                    plan_data["variety"] = line.split(":")[1].strip()
                elif "Rendement estimé" in line and ":" in line:
                    try:
                        yield_str = line.split(":")[1].strip()
                        yield_value = float(
                            "".join(filter(str.isdigit, yield_str.split()[0]))
                        )
                        if yield_value > 0:
                            plan_data["estimated_yield"] = yield_value
                    except:
                        pass
                elif "Budget" in line and ":" in line:
                    try:
                        cost_str = line.split(":")[1].strip()
                        cost_value = float(
                            "".join(filter(str.isdigit, cost_str.split()[0]))
                        )
                        if cost_value > 0:
                            plan_data["estimated_cost"] = cost_value
                    except:
                        pass
                elif "Risques" in line and ":" in line:
                    risks = line.split(":")[1].strip().split(",")
                    if risks:
                        plan_data["risk_factors"] = [
                            risk.strip() for risk in risks if risk.strip()
                        ]

            return plan_data

        except Exception as e:
            print(f"Erreur de parsing: {str(e)}")
            # En cas d'erreur, retourner un plan par défaut
            return {
                "crop_name": "maïs",
                "variety": "Hybride résistant",
                "planting_date": datetime(current_date.year, 5, 1),
                "expected_harvest_date": datetime(current_date.year, 10, 1),
                "required_equipment": [
                    "Tracteur",
                    "Charrue",
                    "Herse",
                    "Semoir",
                    "Système d'irrigation",
                    "Pulvérisateur",
                    "Moissonneuse",
                ],
                "estimated_yield": 8.5,
                "estimated_cost": 100000.0,
                "risk_factors": [
                    "Sécheresse",
                    "Maladies fongiques",
                    "Ravageurs",
                    "Variations climatiques",
                ],
            }

    def _parse_equipment_optimization(self, response: str) -> Dict:
        """Parse la réponse de l'AI pour l'optimisation des équipements"""
        try:
            optimization = {
                "planning": {},
                "maintenance": [],
                "couts": {},
                "suggestions": [],
                "plan_secours": [],
            }

            current_section = None
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if "Planning" in line:
                    current_section = "planning"
                elif "maintenance" in line.lower():
                    current_section = "maintenance"
                elif "coût" in line.lower():
                    current_section = "couts"
                elif "suggestion" in line.lower():
                    current_section = "suggestions"
                elif "secours" in line.lower():
                    current_section = "plan_secours"
                elif line and current_section:
                    if current_section in [
                        "maintenance",
                        "suggestions",
                        "plan_secours",
                    ]:
                        optimization[current_section].append(line)
                    else:
                        key = line.split(":")[0].strip() if ":" in line else line
                        value = line.split(":")[1].strip() if ":" in line else ""
                        optimization[current_section][key] = value

            return optimization
        except Exception as e:
            print(f"Erreur de parsing: {str(e)}")
            return {
                "planning": {
                    "Tracteur": "Utilisation quotidienne",
                    "Semoir": "Période de semis",
                    "Irrigation": "Selon les besoins",
                },
                "maintenance": [
                    "Vérification hebdomadaire des tracteurs",
                    "Entretien mensuel du système d'irrigation",
                ],
                "couts": {"carburant": "5000 €/mois", "maintenance": "2000 €/mois"},
                "suggestions": [
                    "Optimiser les trajets des tracteurs",
                    "Programmer l'irrigation la nuit",
                ],
                "plan_secours": [
                    "Location de tracteur en cas de panne",
                    "Système d'irrigation de secours",
                ],
            }

    def _assess_risk_level(self, risk_factors: List[str]) -> str:
        """Évalue le niveau de risque global"""
        risk_score = len(risk_factors)
        if risk_score <= 2:
            return "Faible"
        elif risk_score <= 4:
            return "Moyen"
        else:
            return "Élevé"

    def analyze_initial_vision(self, project_type, vision):
        """Analyse la vision initiale et génère des questions pertinentes."""
        prompt = f"""En tant qu'expert agricole, analysez cette vision de projet {project_type}:

        Vision: {vision}

        Générez 3-5 questions pertinentes pour mieux comprendre:
        1. Les aspects techniques spécifiques
        2. Les contraintes potentielles
        3. Les opportunités locales
        4. Les objectifs de durabilité

        Concentrez-vous sur les éléments qui permettront d'optimiser le projet."""

        response = self.model.generate_content(prompt)
        questions = response.text.split("\n")
        return [q.strip("- ") for q in questions if q.strip()]

    def analyze_response(self, project_data, user_response):
        """Analyse la réponse de l'utilisateur et génère de nouvelles questions si nécessaire."""
        prompt = f"""Analysez cette réponse pour un projet {project_data['type']}:

        Contexte du projet: {project_data['vision']}
        Réponse de l'utilisateur: {user_response}

        Identifiez les aspects qui nécessitent plus de précisions pour optimiser le projet.
        Générez de nouvelles questions pertinentes si nécessaire."""

        response = self.model.generate_content(prompt)
        if "QUESTIONS SUPPLÉMENTAIRES" in response.text.upper():
            questions = response.text.split("\n")
            return [q.strip("- ") for q in questions if q.strip() and "?" in q]
        return []

    def analyze_environment(
        self, location, climate_data, soil_analysis, water_source, environmental_notes
    ):
        """Analyse les conditions environnementales locales."""
        prompt = f"""Analysez ces conditions environnementales pour un projet agricole:

        Localisation: {location}
        Source d'eau: {water_source}
        Notes environnementales: {environmental_notes}

        Fournissez une analyse détaillée des:
        1. Opportunités environnementales
        2. Contraintes à considérer
        3. Recommandations d'adaptation
        4. Pratiques durables appropriées"""

        response = self.model.generate_content(prompt)
        return {
            "analysis": response.text,
            "location": location,
            "water_source": water_source,
            "notes": environmental_notes,
        }

    def generate_optimized_plan(self, project_data):
        """Génère un plan optimisé basé sur toutes les données collectées."""
        prompt = f"""Créez un plan agricole optimisé pour ce projet:

        Type: {project_data['type']}
        Vision: {project_data['vision']}
        Environnement: {project_data.get('environment', {})}

        Incluez:
        1. Objectifs optimisés
        2. Adaptations environnementales
        3. Gestion des ressources
        4. Calendrier cultural adapté
        5. Innovations recommandées
        6. Questions en suspens

        Basez les recommandations sur les meilleures pratiques agricoles et la durabilité."""

        response = self.model.generate_content(prompt)
        plan_text = response.text

        # Structuration du plan
        plan = {
            "objectives": [],
            "environmental": {"climate_adaptations": [], "resource_management": []},
            "operational": {"calendar": ""},
            "innovations": [],
            "pending_questions": [],
        }

        # Parsing du texte de réponse pour remplir la structure
        sections = plan_text.split("\n\n")
        for section in sections:
            if "OBJECTIFS" in section.upper():
                plan["objectives"] = [
                    obj.strip("- ") for obj in section.split("\n")[1:] if obj.strip()
                ]
            elif "ADAPTATIONS" in section.upper():
                plan["environmental"]["climate_adaptations"] = [
                    adapt.strip("- ")
                    for adapt in section.split("\n")[1:]
                    if adapt.strip()
                ]
            elif "RESSOURCES" in section.upper():
                plan["environmental"]["resource_management"] = [
                    res.strip("- ") for res in section.split("\n")[1:] if res.strip()
                ]
            elif "CALENDRIER" in section.upper():
                plan["operational"]["calendar"] = "\n".join(section.split("\n")[1:])
            elif "INNOVATIONS" in section.upper():
                plan["innovations"] = [
                    innov.strip("- ")
                    for innov in section.split("\n")[1:]
                    if innov.strip()
                ]
            elif "QUESTIONS" in section.upper():
                plan["pending_questions"] = [
                    q.strip("- ") for q in section.split("\n")[1:] if q.strip()
                ]

        return plan

    def analyze_location_potential(self, country, region):
        """Analyse le potentiel agricole d'une région spécifique."""
        prompt = f"""En tant qu'expert agricole, analysez le potentiel agricole de cette région:

        Pays: {country}
        Région: {region}

        Fournissez une analyse détaillée incluant:
        1. Climat et conditions météorologiques typiques
        2. Types de sols dominants
        3. Ressources en eau disponibles
        4. Cultures traditionnelles de la région
        5. Nouvelles opportunités agricoles
        6. Défis environnementaux spécifiques
        7. Infrastructures agricoles existantes
        8. Marchés potentiels
        9. Subventions et programmes de soutien disponibles
        10. Réglementations agricoles importantes

        Basez l'analyse sur les données géographiques et climatiques réelles."""

        response = self.model.generate_content(prompt)
        return self._parse_location_analysis(response.text)

    def suggest_optimal_projects(self, location_analysis):
        """Suggère des projets agricoles optimaux basés sur l'analyse de la localisation."""
        prompt = f"""Basé sur cette analyse régionale:

        {location_analysis}

        Proposez 3-5 projets agricoles optimaux qui:
        1. Maximisent le potentiel local
        2. Sont adaptés aux conditions climatiques
        3. Répondent aux besoins du marché
        4. Sont durables et résilients
        5. Ont un bon potentiel de rentabilité

        Pour chaque projet, détaillez:
        - Description du projet
        - Avantages spécifiques à la région
        - Innovations possibles
        - Estimation du potentiel de réussite
        - Investissement initial estimé
        - Retour sur investissement estimé"""

        response = self.model.generate_content(prompt)
        return self._parse_project_suggestions(response.text)

    def generate_detailed_project(self, project, location_analysis):
        """Génère un plan détaillé pour un projet spécifique."""
        prompt = f"""Créez un plan détaillé pour ce projet agricole:

        Projet: {project['name']}
        Description: {project['description']}

        Analyse régionale:
        {location_analysis}

        Fournissez un plan complet incluant:
        1. Étapes de mise en œuvre détaillées
        2. Calendrier agricole optimisé pour la région
        3. Besoins en ressources spécifiques
        4. Technologies et innovations recommandées
        5. Stratégies de commercialisation adaptées
        6. Plan de gestion des risques climatiques
        7. Mesures de durabilité
        8. Indicateurs de performance clés
        9. Budget détaillé
        10. Plan de croissance sur 5 ans"""

        response = self.model.generate_content(prompt)
        return self._parse_detailed_plan(response.text)

    def _parse_location_analysis(self, analysis_text):
        """Parse l'analyse de localisation en structure de données."""
        analysis = {
            "climate": [],
            "soil": [],
            "water_resources": [],
            "traditional_crops": [],
            "opportunities": [],
            "challenges": [],
            "infrastructure": [],
            "markets": [],
            "support_programs": [],
            "regulations": [],
        }

        current_section = None
        for line in analysis_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if "CLIMAT" in line.upper():
                current_section = "climate"
            elif "SOL" in line.upper():
                current_section = "soil"
            elif "EAU" in line.upper():
                current_section = "water_resources"
            elif "TRADITIONNEL" in line.upper():
                current_section = "traditional_crops"
            elif "OPPORTUNITÉ" in line.upper():
                current_section = "opportunities"
            elif "DÉFI" in line.upper():
                current_section = "challenges"
            elif "INFRASTRUCTURE" in line.upper():
                current_section = "infrastructure"
            elif "MARCHÉ" in line.upper():
                current_section = "markets"
            elif "SOUTIEN" in line.upper() or "SUBVENTION" in line.upper():
                current_section = "support_programs"
            elif "RÉGLEMENT" in line.upper():
                current_section = "regulations"
            elif current_section and line.startswith("-"):
                analysis[current_section].append(line.strip("- "))

        return analysis

    def suggest_optimal_projects(self, location_analysis):
        """Suggère des projets agricoles optimaux basés sur l'analyse de la localisation."""
        prompt = f"""Basé sur cette analyse régionale:

        {location_analysis}

        Proposez 3-5 projets agricoles optimaux qui:
        1. Maximisent le potentiel local
        2. Sont adaptés aux conditions climatiques
        3. Répondent aux besoins du marché
        4. Sont durables et résilients
        5. Ont un bon potentiel de rentabilité

        Pour chaque projet, détaillez:
        - Description du projet
        - Avantages spécifiques à la région
        - Innovations possibles
        - Estimation du potentiel de réussite
        - Investissement initial estimé
        - Retour sur investissement estimé"""

        response = self.model.generate_content(prompt)
        return self._parse_project_suggestions(response.text)

    def _parse_project_suggestions(self, suggestions_text):
        """Parse les suggestions de projets en structure de données."""
        projects = []
        current_project = None

        for line in suggestions_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if (
                line.startswith("Projet")
                or line.startswith("1.")
                or line.startswith("2.")
                or line.startswith("3.")
            ):
                if current_project:
                    projects.append(current_project)
                current_project = {
                    "name": line.split(":")[-1].strip() if ":" in line else line,
                    "description": "",
                    "advantages": [],
                    "innovations": [],
                    "success_potential": "",
                    "initial_investment": "",
                    "roi": "",
                }
            elif current_project:
                if "AVANTAGES" in line.upper():
                    current_section = "advantages"
                elif "INNOVATION" in line.upper():
                    current_section = "innovations"
                elif "POTENTIEL" in line.upper():
                    current_project["success_potential"] = line.split(":")[-1].strip()
                elif "INVESTISSEMENT" in line.upper():
                    current_project["initial_investment"] = line.split(":")[-1].strip()
                elif "RETOUR" in line.upper():
                    current_project["roi"] = line.split(":")[-1].strip()
                elif line.startswith("-"):
                    if current_section == "advantages":
                        current_project["advantages"].append(line.strip("- "))
                    elif current_section == "innovations":
                        current_project["innovations"].append(line.strip("- "))
                else:
                    current_project["description"] += line + " "

        if current_project:
            projects.append(current_project)

        return projects

    def generate_project_analysis(
        self, project_name: str, objective: str, location: str
    ) -> Dict:
        """Génère une analyse détaillée et précise du projet agricole basée sur l'objectif."""
        try:
            # Coordonnées par défaut pour Bujumbura si la localisation n'est pas fournie
            default_coords = {
                "Bujumbura": (-3.3864, 29.3650),
                "Gitega": (-3.4271, 29.9246),
                "Ngozi": (-2.9075, 29.8306),
                "Rumonge": (-3.9736, 29.4386),
                "Bururi": (-3.9486, 29.6244),
            }

            # Obtenir les coordonnées en fonction de la localisation
            latitude, longitude = default_coords.get(
                location, (-3.3864, 29.3650)
            )  # Bujumbura par défaut

            # Collecter les données météorologiques
            weather_data = (
                self.weather_service.get_current_weather(
                    latitude=latitude, longitude=longitude
                )
                or {}
            )

            # Générer le prompt pour l'analyse
            prompt = f"""En tant qu'expert en agriculture au Burundi, analysez cet objectif et générez des recommandations détaillées.

            Objectif du projet :
            {objective}

            Localisation : {location}
            Données météo actuelles : {json.dumps(weather_data, ensure_ascii=False)}

            Générez une analyse complète au format JSON avec exactement cette structure :
            {{
                "type_culture": "culture recommandée en fonction de l'objectif",
                "superficie": "superficie recommandée en hectares",
                "duree": "durée estimée du projet",
                "budget": "budget estimé en FBu",
                "main_oeuvre": "nombre de personnes nécessaires",
                "type_sol": "type de sol recommandé",
                "climat": "conditions climatiques optimales",
                "methode_culture": "méthode de culture recommandée",
                "semences": "types et quantités de semences",
                "engrais": "types d'engrais recommandés",
                "irrigation": "système d'irrigation conseillé",
                "equipements": "liste des équipements nécessaires",
                "planning": "calendrier détaillé des activités",
                "risques_climatiques": "analyse des risques climatiques",
                "risques_biologiques": "analyse des risques de maladies et parasites",
                "solutions_risques": "solutions proposées pour les risques",
                "recommandations": "recommandations détaillées",
                "conclusion": "conclusion générale du projet"
            }}

            Important :
            1. Basez vos recommandations sur les pratiques agricoles locales au Burundi
            2. Tenez compte du climat et de la saison actuelle
            3. Privilégiez des solutions adaptées aux petits agriculteurs
            4. Incluez des techniques durables et rentables
            5. Soyez précis dans les estimations de coûts et de durée"""

            # Générer l'analyse
            response = self.send_message(prompt)

            if response:
                try:
                    return self.parse_json_response(response)
                except Exception as e:
                    print(f"Erreur lors du parsing JSON : {str(e)}")
                    return self._get_default_analysis()
            else:
                print("Pas de réponse du modèle")
                return self._get_default_analysis()

        except Exception as e:
            print(f"Erreur lors de la génération de l'analyse : {str(e)}")
            return self._get_default_analysis()

    def _get_default_analysis(self) -> Dict:
        """Retourne une analyse par défaut en cas d'erreur."""
        return {
            "type_culture": "Non spécifié",
            "superficie": "À définir",
            "duree": "À estimer",
            "budget": "À déterminer",
            "main_oeuvre": "À préciser",
            "type_sol": "À identifier",
            "climat": "À analyser",
            "methode_culture": "À déterminer",
            "semences": "À préciser",
            "engrais": "À déterminer",
            "irrigation": "À préciser",
            "equipements": "À déterminer",
            "planning": "À définir",
            "risques_climatiques": "À analyser",
            "risques_biologiques": "À analyser",
            "solutions_risques": "À déterminer",
            "recommandations": "À préciser",
            "conclusion": "Analyse en attente",
        }

    def create_detailed_project(
        self, objective: str, location: str, analysis: Dict
    ) -> Dict:
        """Crée un projet détaillé avec tous les éléments pratiques nécessaires.

        Args:
            objective: Objectif du projet
            location: Localisation du projet
            analysis: Analyse précédente du projet

        Returns:
            Dict contenant tous les détails pratiques du projet
        """
        try:
            # Obtenir les données météo actuelles
            coords = {
                "Bujumbura": (-3.3864, 29.3650),
                "Gitega": (-3.4271, 29.9246),
                "Ngozi": (-2.9075, 29.8306),
                "Rumonge": (-3.9736, 29.4386),
                "Bururi": (-3.9486, 29.6244),
            }
            latitude, longitude = coords.get(location, (-3.3864, 29.3650))
            weather_data = self.weather_service.get_current_weather(latitude, longitude)

            # Générer le prompt pour la création du projet
            prompt = f"""Tu es un expert agricole au Burundi. Crée un projet détaillé et pratique basé sur ces informations.

            IMPORTANT : Ta réponse doit être UNIQUEMENT un objet JSON valide, sans texte avant ou après.

            Informations du projet :
            - OBJECTIF : {objective}
            - LOCALISATION : {location}
            - ANALYSE : {json.dumps(analysis, ensure_ascii=False)}
            - MÉTÉO : {json.dumps(weather_data, ensure_ascii=False)}

            Format de réponse attendu (à compléter avec des données réelles) :
            {{
                "preparation_terrain": {{
                    "etapes": ["étape 1", "étape 2"],
                    "outils_necessaires": ["outil 1", "outil 2"],
                    "cout_estime": "XXX FBu",
                    "duree_estimee": "X jours"
                }},
                "approvisionnement": {{
                    "semences": {{
                        "type": "type spécifique",
                        "quantite": "X kg",
                        "fournisseurs": ["nom 1", "nom 2"],
                        "cout_estime": "XXX FBu"
                    }},
                    "engrais": {{
                        "types": ["type 1", "type 2"],
                        "quantites": "X kg par type",
                        "fournisseurs": ["nom 1", "nom 2"],
                        "cout_estime": "XXX FBu"
                    }},
                    "equipements": {{
                        "a_acheter": ["item 1", "item 2"],
                        "a_louer": ["item 1", "item 2"],
                        "fournisseurs": ["nom 1", "nom 2"],
                        "cout_estime": "XXX FBu"
                    }}
                }},
                "calendrier_cultural": {{
                    "preparation": {{
                        "debut": "date spécifique",
                        "duree": "X jours",
                        "activites": ["activité 1", "activité 2"]
                    }},
                    "semis": {{
                        "periode_optimale": "période spécifique",
                        "methode": "description précise",
                        "points_cles": ["point 1", "point 2"]
                    }},
                    "entretien": {{
                        "activites_regulieres": ["activité 1", "activité 2"],
                        "frequence": "fréquence spécifique",
                        "points_attention": ["point 1", "point 2"]
                    }},
                    "recolte": {{
                        "periode_estimee": "période spécifique",
                        "methode": "description précise",
                        "stockage": "recommandations spécifiques"
                    }}
                }},
                "ressources_humaines": {{
                    "competences_requises": ["compétence 1", "compétence 2"],
                    "formation_necessaire": ["formation 1", "formation 2"],
                    "nombre_personnes": "X personnes",
                    "cout_estime": "XXX FBu"
                }},
                "gestion_risques": {{
                    "preventions": ["mesure 1", "mesure 2"],
                    "assurance": {{
                        "recommandation": "type spécifique",
                        "cout_estime": "XXX FBu"
                    }},
                    "plan_urgence": ["action 1", "action 2"]
                }},
                "commercialisation": {{
                    "marches_cibles": ["marché 1", "marché 2"],
                    "prix_vente_estime": "XXX FBu par unité",
                    "canaux_distribution": ["canal 1", "canal 2"],
                    "stockage_transport": "solutions spécifiques"
                }},
                "suivi_evaluation": {{
                    "indicateurs": ["indicateur 1", "indicateur 2"],
                    "outils_suivi": ["outil 1", "outil 2"],
                    "frequence_evaluation": "fréquence spécifique"
                }},
                "budget_total": {{
                    "investissement_initial": "XXX FBu",
                    "couts_operationnels": "XXX FBu par mois",
                    "revenus_prevus": "XXX FBu",
                    "retour_investissement": "X mois"
                }},
                "contacts_utiles": {{
                    "experts_agricoles": ["nom et contact 1", "nom et contact 2"],
                    "fournisseurs": ["nom et contact 1", "nom et contact 2"],
                    "institutions": ["nom et contact 1", "nom et contact 2"],
                    "acheteurs": ["nom et contact 1", "nom et contact 2"]
                }}
            }}

            RÈGLES IMPORTANTES :
            1. Réponds UNIQUEMENT avec le JSON, sans texte avant ou après
            2. Assure-toi que le JSON est valide (pas de virgules en trop ou manquantes)
            3. Utilise des valeurs RÉELLES et PRÉCISES pour le Burundi
            4. Tous les coûts doivent être en Francs Burundais (FBu)
            5. Inclus des noms et contacts RÉELS quand possible"""

            # Générer le projet détaillé
            response = self.send_message(prompt)

            if response:
                try:
                    project_data = self.parse_json_response(response)
                    # Valider la structure du projet
                    return self._validate_project_structure(project_data)
                except Exception as e:
                    print(f"Erreur lors du parsing JSON : {str(e)}")
                    return self._get_default_project()
            else:
                print("Pas de réponse du modèle")
                return self._get_default_project()

        except Exception as e:
            print(f"Erreur lors de la création du projet : {str(e)}")
            return self._get_default_project()

    def _validate_project_structure(self, project_data: Dict) -> Dict:
        """Valide et complète la structure du projet si nécessaire."""
        required_structure = {
            "preparation_terrain": {
                "etapes": [],
                "outils_necessaires": [],
                "cout_estime": "À estimer",
                "duree_estimee": "À définir",
            },
            "approvisionnement": {
                "semences": {
                    "type": "À définir",
                    "quantite": "À définir",
                    "fournisseurs": [],
                    "cout_estime": "À estimer",
                },
                "engrais": {
                    "types": [],
                    "quantites": "À définir",
                    "fournisseurs": [],
                    "cout_estime": "À estimer",
                },
                "equipements": {
                    "a_acheter": [],
                    "a_louer": [],
                    "fournisseurs": [],
                    "cout_estime": "À estimer",
                },
            },
            "calendrier_cultural": {
                "preparation": {
                    "debut": "À définir",
                    "duree": "À définir",
                    "activites": [],
                },
                "semis": {
                    "periode_optimale": "À définir",
                    "methode": "À définir",
                    "points_cles": [],
                },
                "entretien": {
                    "activites_regulieres": [],
                    "frequence": "À définir",
                    "points_attention": [],
                },
                "recolte": {
                    "periode_estimee": "À définir",
                    "methode": "À définir",
                    "stockage": "À définir",
                },
            },
            "ressources_humaines": {
                "competences_requises": [],
                "formation_necessaire": [],
                "nombre_personnes": "À définir",
                "cout_estime": "À estimer",
            },
            "gestion_risques": {
                "preventions": [],
                "assurance": {
                    "recommandation": "À définir",
                    "cout_estime": "À estimer",
                },
                "plan_urgence": [],
            },
            "commercialisation": {
                "marches_cibles": [],
                "prix_vente_estime": "À estimer",
                "canaux_distribution": [],
                "stockage_transport": "À définir",
            },
            "suivi_evaluation": {
                "indicateurs": [],
                "outils_suivi": [],
                "frequence_evaluation": "À définir",
            },
            "budget_total": {
                "investissement_initial": "À estimer",
                "couts_operationnels": "À estimer",
                "revenus_prevus": "À estimer",
                "retour_investissement": "À estimer",
            },
            "contacts_utiles": {
                "experts_agricoles": [],
                "fournisseurs": [],
                "institutions": [],
                "acheteurs": [],
            },
        }

        # Fonction récursive pour valider et compléter la structure
        def validate_dict(template: Dict, data: Dict) -> Dict:
            result = {}
            for key, value in template.items():
                if key not in data:
                    result[key] = value
                elif isinstance(value, dict):
                    result[key] = validate_dict(value, data.get(key, {}))
                elif isinstance(value, list):
                    result[key] = (
                        data.get(key, []) if isinstance(data.get(key), list) else value
                    )
                else:
                    result[key] = data.get(key, value)
            return result

        # Valider et compléter la structure
        validated_project = validate_dict(required_structure, project_data)

        return validated_project

    def _get_default_project(self) -> Dict:
        """Retourne un projet par défaut en cas d'erreur."""
        return {
            "preparation_terrain": {
                "etapes": ["À définir"],
                "outils_necessaires": ["À définir"],
                "cout_estime": "À estimer",
                "duree_estimee": "À définir",
            },
            "approvisionnement": {
                "semences": {
                    "type": "À définir",
                    "quantite": "À définir",
                    "fournisseurs": ["À identifier"],
                    "cout_estime": "À estimer",
                },
                "engrais": {
                    "types": ["À définir"],
                    "quantites": "À définir",
                    "fournisseurs": ["À identifier"],
                    "cout_estime": "À estimer",
                },
                "equipements": {
                    "a_acheter": ["À définir"],
                    "a_louer": ["À définir"],
                    "fournisseurs": ["À identifier"],
                    "cout_estime": "À estimer",
                },
            },
            "calendrier_cultural": {
                "preparation": {
                    "debut": "À définir",
                    "duree": "À définir",
                    "activites": ["À planifier"],
                },
                "semis": {
                    "periode_optimale": "À définir",
                    "methode": "À définir",
                    "points_cles": ["À définir"],
                },
                "entretien": {
                    "activites_regulieres": ["À définir"],
                    "frequence": "À définir",
                    "points_attention": ["À définir"],
                },
                "recolte": {
                    "periode_estimee": "À définir",
                    "methode": "À définir",
                    "stockage": "À définir",
                },
            },
            "ressources_humaines": {
                "competences_requises": ["À définir"],
                "formation_necessaire": ["À définir"],
                "nombre_personnes": "À définir",
                "cout_estime": "À estimer",
            },
            "gestion_risques": {
                "preventions": ["À définir"],
                "assurance": {
                    "recommandation": "À définir",
                    "cout_estime": "À estimer",
                },
                "plan_urgence": ["À définir"],
            },
            "commercialisation": {
                "marches_cibles": ["À identifier"],
                "prix_vente_estime": "À estimer",
                "canaux_distribution": ["À définir"],
                "stockage_transport": "À définir",
            },
            "suivi_evaluation": {
                "indicateurs": ["À définir"],
                "outils_suivi": ["À définir"],
                "frequence_evaluation": "À définir",
            },
            "budget_total": {
                "investissement_initial": "À estimer",
                "couts_operationnels": "À estimer",
                "revenus_prevus": "À estimer",
                "retour_investissement": "À estimer",
            },
            "contacts_utiles": {
                "experts_agricoles": ["À identifier"],
                "fournisseurs": ["À identifier"],
                "institutions": ["À identifier"],
                "acheteurs": ["À identifier"],
            },
        }

    def parse_json_response(self, response: str) -> Dict:
        """Parse la réponse JSON de l'IA avec gestion améliorée des erreurs."""
        try:
            # Nettoyer la réponse
            # Trouver le premier { et le dernier }
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                print("Aucun JSON trouvé dans la réponse")
                return {}

            # Extraire seulement la partie JSON
            json_str = response[start:end]

            # Nettoyer les caractères problématiques
            json_str = json_str.replace("\n", " ")
            json_str = json_str.replace("\r", " ")
            json_str = " ".join(json_str.split())  # Normaliser les espaces

            # Tentative de parsing
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Première tentative de parsing échouée : {str(e)}")

                # Deuxième tentative : nettoyage plus agressif
                # Supprimer les commentaires potentiels
                json_lines = json_str.split("\n")
                json_lines = [
                    line for line in json_lines if not line.strip().startswith("//")
                ]
                json_str = "\n".join(json_lines)

                # Supprimer les virgules trailing
                json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

                # Ajouter les virgules manquantes entre les objets
                json_str = re.sub(r"}\s*{", "},{", json_str)

                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Deuxième tentative de parsing échouée : {str(e)}")
                    print("Réponse problématique :")
                    print(json_str)
                    return {}

        except Exception as e:
            print(f"Erreur lors du parsing de la réponse : {str(e)}")
            return {}
