"""
LangGraph Orchestrator.

Constructs and compiles the AI agent workflow graph for processing leads.
"""
from langgraph.graph import StateGraph, END
from app.agents.state import LeadState
from app.agents.nodes.ingestion import extract_lead
from app.agents.nodes.profiling import profile_customer
from app.agents.nodes.matching import recommend_products
from app.agents.nodes.briefing import generate_brief
from app.agents.nodes.auditor import validate_fields
from app.agents.nodes.outreach import generate_outreach
from app.agents.nodes.doc_intel import verify_documents
from app.agents.nodes.underwriting import calculate_eligibility

import logging
logger = logging.getLogger(__name__)

def with_logging(node_name, node_func):
    def wrapper(state: LeadState):
        import json
        logger.info(f"==========> [AGENT STARTING]: {node_name}")
        
        # Capture state before
        state_before = {k: v for k, v in state.items()}
        
        try:
            result = node_func(state)
        except Exception as e:
            logger.error(f"Error in agent {node_name}: {e}", exc_info=True)
            raise e
        
        # Find changes
        changes = {}
        for k, v in result.items():
            if k not in state_before or state_before[k] != v:
                changes[k] = v
                
        logger.info(f"<========== [AGENT FINISHED]: {node_name}")
        if changes:
            logger.info(f"📤 [UPDATED FIELDS in {node_name}]:")
            for k, v in changes.items():
                val_str = str(v)
                if len(val_str) > 200:
                    val_str = val_str[:200] + "... [truncated]"
                logger.info(f"   - {k}: {val_str}")
        else:
            logger.info(f"📤 [NO FIELDS UPDATED in {node_name}]")
        return result
    return wrapper

def create_graph():
    workflow = StateGraph(LeadState)

    workflow.add_node("extract_lead", with_logging("Ingestion Agent (extract_lead)", extract_lead))
    workflow.add_node("profile_customer", with_logging("Profiling Agent (profile_customer)", profile_customer))
    workflow.add_node("recommend_products", with_logging("Matching Agent (recommend_products)", recommend_products))
    workflow.add_node("generate_brief", with_logging("Briefing Agent (generate_brief)", generate_brief))
    workflow.add_node("validate_fields", with_logging("Auditor Agent (validate_fields)", validate_fields))
    workflow.add_node("generate_outreach", with_logging("Outreach Agent (generate_outreach)", generate_outreach))
    workflow.add_node("verify_documents", with_logging("Doc Intel Agent (verify_documents)", verify_documents))
    workflow.add_node("calculate_eligibility", with_logging("Underwriting Agent (calculate_eligibility)", calculate_eligibility))

    workflow.add_edge("extract_lead", "profile_customer")
    workflow.add_edge("profile_customer", "recommend_products")
    workflow.add_edge("recommend_products", "generate_brief")
    workflow.add_edge("generate_brief", "validate_fields")

    def route_after_validation(state: LeadState):
        if not state.get("is_profile_complete"):
            return "generate_outreach"
        return "calculate_eligibility"

    workflow.add_conditional_edges(
        "validate_fields",
        route_after_validation,
        {
            "generate_outreach": "generate_outreach",
            "calculate_eligibility": "calculate_eligibility"
        }
    )

    workflow.add_edge("generate_outreach", END)
    
    workflow.add_edge("verify_documents", "calculate_eligibility")
    workflow.add_edge("calculate_eligibility", END)
    
    workflow.set_entry_point("extract_lead")

    return workflow.compile()

graph = create_graph()
