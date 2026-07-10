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

def create_graph():
    workflow = StateGraph(LeadState)

    workflow.add_node("extract_lead", extract_lead)
    workflow.add_node("profile_customer", profile_customer)
    workflow.add_node("recommend_products", recommend_products)
    workflow.add_node("generate_brief", generate_brief)
    workflow.add_node("validate_fields", validate_fields)
    workflow.add_node("generate_outreach", generate_outreach)
    workflow.add_node("verify_documents", verify_documents)
    workflow.add_node("calculate_eligibility", calculate_eligibility)

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
