import os
import logging
from typing import Dict, Any, Optional, List
import json
import google.generativeai as genai

logger = logging.getLogger(__name__)

class BaseAgent:
    """Classe de base pour tous les agents utilisant l'IA."""
    
    def __init__(self, api_key: str):
        """Initialise l'agent avec une clé API.
        
        Args:
            api_key: Clé API pour le modèle Gemini
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.chat_session = self.model.start_chat(history=[])
    
    def send_message(self, message: str) -> str:
        """Envoie un message au modèle et retourne la réponse.
        
        Args:
            message: Message à envoyer au modèle
            
        Returns:
            Réponse du modèle
        """
        try:
            # Configuration du modèle pour une réponse structurée
            response = self.model.generate_content(
                message,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            if not response.text:
                raise ValueError("Réponse vide du modèle")
                
            print(f"Réponse brute du modèle : {response.text}")
            return response.text
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du message : {str(e)}")
            return ""
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse une réponse JSON du modèle.
        
        Args:
            response: Réponse du modèle à parser
            
        Returns:
            Dictionnaire contenant les données parsées
        """
        try:
            # Nettoyer la réponse
            cleaned_response = response.strip()
            
            # Trouver le début et la fin du JSON
            start = cleaned_response.find('{')
            end = cleaned_response.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise ValueError("Aucun JSON trouvé dans la réponse")
            
            # Extraire et parser le JSON
            json_str = cleaned_response[start:end]
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Erreur lors du parsing JSON : {str(e)}")
            return {}
