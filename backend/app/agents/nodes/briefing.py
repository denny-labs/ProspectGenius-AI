"""
Briefing Node.

Uses the LLM to generate a concise, 20-second executive summary of the lead
to help Relationship Managers instantly grasp the customer's intent.
"""
import json
from app.orchestration.llm import get_llm
from app.agents.state import LeadState
from app.orchestration.prompts.prompt import BRIEFING_PROMPT
from app.config import settings

def generate_brief(state: LeadState) -> LeadState:
    """
    Synthesizes a 20-second executive summary of the lead for the RM.
    
    Args:
        state (LeadState): The current state of the lead.
        
    Returns:
        LeadState: The updated state containing the 'ai_20_sec_summary'.
    """
    llm = get_llm(temperature=0.7)
    if not llm:
        state["ai_20_sec_summary"] = "Customer requires a loan. Budget and details are being gathered."
        return state
        
    profile_str = json.dumps({k: v for k, v in state.items() if v is not None and type(v) in [str, int, float, bool]}, default=str)
    prompt = BRIEFING_PROMPT.format(profile=profile_str)
    
    try:
        response = llm.invoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = " ".join([item.get("text", "") for item in content if isinstance(item, dict)])
        elif not isinstance(content, str):
            content = str(content)
            
        state["ai_20_sec_summary"] = content.strip()
    except Exception as e:
        print(f"Briefing error: {e}")
            
    return state
