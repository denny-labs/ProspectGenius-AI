"""
Outreach Node.

Generates personalized drafts (e.g., WhatsApp, Email) using specific channels and tones
to politely request missing documentation from the customer.
"""
import json
import re
from app.orchestration.llm import get_llm
from app.agents.state import LeadState
from app.orchestration.prompts.prompt import OUTREACH_PROMPT

def generate_outreach(state: LeadState) -> LeadState:
    """
    Drafts highly personalized WhatsApp, Email, or SMS outreach messages.
    
    Args:
        state (LeadState): The current state of the lead.
        
    Returns:
        LeadState: The updated state containing 'rm_whatsapp_draft' and 'rm_phone_script'.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"==========> [OUTREACH AGENT STARTING] Lead ID: {state.get('lead_id')}")
    
    llm = get_llm(temperature=0.7)
    if not llm:
        logger.warning("[OUTREACH AGENT] No LLM configured. Falling back to default script.")
        state["rm_phone_script"] = "Hi, calling to request missing details for your application."
        state["rm_whatsapp_draft"] = "Hello! Please share your missing documents."
        return state
        
    profile_str = json.dumps({k: v for k, v in state.items() if v is not None and type(v) in [str, int, float, bool]}, default=str)
    
    channel = state.get("draft_channel", "WhatsApp")
    tone = state.get("draft_tone", "Professional")
    
    prompt = OUTREACH_PROMPT.format(
        profile=profile_str, 
        missing_fields=", ".join(state.get("missing_fields", [])),
        channel=channel,
        tone=tone
    )
    
    logger.debug(f"[OUTREACH AGENT] Constructed Prompt for LLM:\n{prompt}")
    
    try:
        logger.info("[OUTREACH AGENT] Sending request to LLM...")
        response = llm.invoke(prompt)
        content = response.content
        logger.debug(f"[OUTREACH AGENT] Raw LLM Response:\n{content}")
        
        if isinstance(content, list):
            content = " ".join([item.get("text", "") for item in content if isinstance(item, dict)])
        elif not isinstance(content, str):
            content = str(content)
            
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            if "rm_phone_script" in data:
                state["rm_phone_script"] = data["rm_phone_script"]
                logger.info("[OUTREACH AGENT] Successfully parsed rm_phone_script.")
            if "rm_whatsapp_draft" in data:
                state["rm_whatsapp_draft"] = data["rm_whatsapp_draft"]
                logger.info("[OUTREACH AGENT] Successfully parsed rm_whatsapp_draft.")
        else:
            logger.error("[OUTREACH AGENT] Failed to parse JSON from LLM response.")
            
    except Exception as e:
        logger.error(f"[OUTREACH AGENT] Error generating outreach: {e}", exc_info=True)
            
    logger.info(f"<========== [OUTREACH AGENT FINISHED] Lead ID: {state.get('lead_id')}")
    return state
