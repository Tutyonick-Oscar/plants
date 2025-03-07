from typing import Dict, List

from agents.monitoring_agent import MonitoringAgent
from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from pydantic import BaseModel, Field


class CoordinatorAgent(BaseModel):
    api_key: str = Field(..., description="API key for Gemini")
    planning_agent: PlanningAgent = None
    monitoring_agent: MonitoringAgent = None
    research_agent: ResearchAgent = None

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.planning_agent = PlanningAgent(api_key=self.api_key)
        self.monitoring_agent = MonitoringAgent(api_key=self.api_key)
        self.research_agent = ResearchAgent(api_key=self.api_key)

    def execute_workflow(self, state: Dict) -> Dict:
        """Exécute le workflow complet"""
        # Phase de recherche
        state = self.research_phase(state)

        # Phase de planification
        state = self.planning_phase(state)

        # Phase de surveillance initiale
        state = self.monitoring_phase(state)

        # Phase d'optimisation
        state = self.optimization_phase(state)

        # Décision finale
        final_decision = self.make_decision(state)
        state["final_decision"] = final_decision

        return state

    def research_phase(self, state: Dict) -> Dict:
        """Coordonne la phase de recherche"""
        # Recherche des données expertes
        expert_data = self.research_agent.search_agricultural_data(
            state["crop_type"], state.get("region", "default_region")
        )

        # Obtention des prévisions météo
        weather_forecast = self.research_agent.get_weather_forecast(
            state.get("location", {"latitude": 0, "longitude": 0})
        )

        return {
            **state,
            "expert_data": expert_data,
            "weather_forecast": weather_forecast,
        }

    def planning_phase(self, state: Dict) -> Dict:
        """Coordonne la phase de planification"""
        analysis = self.planning_agent.analyze_requirements(
            state["target_yield"], state["crop_type"]
        )

        plan = self.planning_agent.create_cultivation_plan(
            analysis, state["weather_forecast"]
        )

        return {**state, "analysis": analysis, "cultivation_plan": plan}

    def monitoring_phase(self, state: Dict) -> Dict:
        """Coordonne la phase de surveillance"""
        sensor_analysis = self.monitoring_agent.analyze_sensor_data(
            state.get("sensor_data", {})
        )

        recommendations = self.monitoring_agent.recommend_actions(sensor_analysis)

        return {
            **state,
            "sensor_analysis": sensor_analysis,
            "recommendations": recommendations,
        }

    def optimization_phase(self, state: Dict) -> Dict:
        """Coordonne la phase d'optimisation"""
        optimization_strategy = self.research_agent.optimize_yield_strategy(
            state["target_yield"],
            {
                "sensor_data": state.get("sensor_data", {}),
                "weather_forecast": state.get("weather_forecast", {}),
                "expert_data": state.get("expert_data", {}),
            },
        )

        return {**state, "optimization_strategy": optimization_strategy}

    def make_decision(self, state: Dict) -> str:
        """Prend une décision basée sur l'état actuel"""
        if state.get("sensor_analysis", {}).get("alerts", []):
            return "continue_monitoring"

        # Vérifier si l'optimisation est nécessaire
        current_yield_potential = (
            state.get("optimization_strategy", {})
            .get("yield_potential", {})
            .get("potential_yield", 0)
        )
        if current_yield_potential < state["target_yield"]:
            return "optimize"

        return "complete"
