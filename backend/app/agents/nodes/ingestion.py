"""
Ingestion Node.

Extracts structured JSON fields from raw, unstructured user text using the LLM.
"""
import json
import re
from app.agents.state import LeadState
from app.orchestration.prompts.prompt import INGESTION_PROMPT
from app.orchestration.llm import get_llm

def extract_lead(state: LeadState, raw_text: str = "") -> LeadState:
    """
    Extracts structured lead data from unstructured raw text using the LLM.
    
    Args:
        state (LeadState): The current state of the lead.
        raw_text (str, optional): The raw text to process. Defaults to "".
        
    Returns:
        LeadState: The updated state containing extracted fields (e.g., name, income).
    """
    llm = get_llm(temperature=0.0)
    if not llm or not raw_text:
        return state
        
    prompt = INGESTION_PROMPT.format(text=raw_text)
    
    try:
        response = llm.invoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = " ".join([item.get("text", "") for item in content if isinstance(item, dict)])
        elif not isinstance(content, str):
            content = str(content)
            
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            for k, v in data.items():
                if k in LeadState.__annotations__:
                    state[k] = v
    except Exception as e:
        print(f"Ingestion error: {e}")
            
    return state
