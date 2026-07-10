"""
Matching Node.

Uses the LLM to suggest primary and secondary banking products based on
the customer's profile, intent, and demographic data.
"""
import json
import re
from app.orchestration.llm import get_llm
from app.agents.state import LeadState
from app.orchestration.prompts.prompt import MATCHING_PROMPT
from app.config import settings

def recommend_products(state: LeadState) -> LeadState:
    """
    Recommends primary and secondary banking products tailored to the lead's profile.
    
    Args:
        state (LeadState): The current state of the lead.
        
    Returns:
        LeadState: The updated state with recommended banking products.
    """
    llm = get_llm(temperature=0.0)
    if not llm:
        state["primary_product"] = "Personal Loan"
        state["secondary_products"] = []
        return state
        
    profile_str = json.dumps({k: v for k, v in state.items() if v is not None and type(v) in [str, int, float, bool]}, default=str)
    prompt = MATCHING_PROMPT.format(profile=profile_str)
    
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
            if "primary_product" in data:
                state["primary_product"] = data["primary_product"]
            if "secondary_products" in data:
                state["secondary_products"] = data["secondary_products"]
    except Exception as e:
        print(f"Matching error: {e}")
            
    return state
