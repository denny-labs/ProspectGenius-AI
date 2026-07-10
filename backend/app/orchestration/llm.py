"""
LLM Orchestration module.

Provides a centralized factory function to instantiate and configure
the Google Gemini generative model across the backend.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

def get_llm(temperature: float = 0.0):
    """
    Initializes and returns the Google Gemini LLM instance.
    
    Args:
        temperature (float, optional): The sampling temperature. Defaults to 0.0.
        
    Returns:
        ChatGoogleGenerativeAI or None: The initialized LLM, or None if no API key is found.
    """
    if not settings.GOOGLE_API_KEY:
        return None
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL, 
        google_api_key=settings.GOOGLE_API_KEY, 
        temperature=temperature
    )
