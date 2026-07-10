"""
Profiling Node.

Uses the LLM to analyze the lead's qualitative data to generate a quantitative
lead score, buying intent, urgency level, and risk level.
"""
import json
import re
from app.orchestration.llm import get_llm
from app.agents.state import LeadState
from app.orchestration.prompts.prompt import PROFILING_PROMPT
from app.config import settings

def profile_customer(state: LeadState) -> LeadState:
    """
    Analyzes qualitative lead data to generate quantitative intent and risk scores.
    
    Args:
        state (LeadState): The current state of the lead.
        
    Returns:
        LeadState: The updated state containing lead_score, urgency, and risk metrics.
    """
    llm = get_llm(temperature=0.0)
    if not llm:
        state["lead_score"] = 50
        state["buying_intent"] = "Medium"
        state["urgency"] = "Medium"
        state["risk_level"] = "Medium"
        return state
        
    profile_str = json.dumps({k: v for k, v in state.items() if v is not None and type(v) in [str, int, float, bool]}, default=str)
    prompt = PROFILING_PROMPT.format(profile=profile_str)
    
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
        print(f"Profiling error: {e}")
            
    return state
