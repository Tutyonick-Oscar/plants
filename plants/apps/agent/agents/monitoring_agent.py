from datetime import datetime
from typing import Dict, List

import google.generativeai as genai
from pydantic import BaseModel, Field


class MonitoringAgent(BaseModel):
    api_key: str = Field(..., description="API key for Gemini")
    model: object = None

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def analyze_sensor_data(self, sensor_data: Dict) -> Dict:
        """Analyzes real-time sensor data from the field"""
        prompt = f"""As an agricultural monitoring expert, analyze the following sensor data:
        Temperature: {sensor_data.get('temperature')}°C
        Soil Moisture: {sensor_data.get('soil_moisture')}%
        Humidity: {sensor_data.get('humidity')}%

        Identify:
        1. Any immediate concerns
        2. Required actions
        3. Optimization opportunities"""

        response = self.model.generate_content(prompt)
        return {
            "analysis": response.text,
            "timestamp": datetime.now().isoformat(),
            "alerts": self._generate_alerts(sensor_data),
        }

    def _generate_alerts(self, sensor_data: Dict) -> List[Dict]:
        """Generates alerts based on sensor data thresholds"""
        alerts = []

        # Example thresholds - these should be customizable per crop
        if sensor_data.get("soil_moisture", 0) < 30:
            alerts.append(
                {
                    "type": "warning",
                    "message": "Low soil moisture detected - irrigation may be needed",
                    "priority": "high",
                }
            )

        if sensor_data.get("temperature", 20) > 35:
            alerts.append(
                {
                    "type": "alert",
                    "message": "High temperature detected - consider protective measures",
                    "priority": "medium",
                }
            )

        return alerts

    def recommend_actions(self, analysis: Dict) -> Dict:
        """Recommends specific actions based on analysis"""
        prompt = f"""Based on the following analysis:
        {analysis}

        Recommend specific actions for:
        1. Immediate intervention if needed
        2. Preventive measures
        3. Optimization steps

        Provide practical, actionable steps."""

        response = self.model.generate_content(prompt)
        return {"recommendations": response.text, "status": "monitoring_complete"}
