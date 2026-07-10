"""
Underwriting Node.

A rules-based engine that calculates FOIR (Fixed Obligation to Income Ratio),
LTV (Loan to Value), eligible loan amounts, and estimates EMIs based on standard banking formulas.
"""
from app.agents.state import LeadState

def calculate_eligibility(state: LeadState) -> LeadState:
    """
    Calculates loan eligibility, Fixed Obligation to Income Ratio (FOIR),
    and Loan to Value (LTV) ratio using standard underwriting rules.
    
    Args:
        state (LeadState): The current state of the lead.
        
    Returns:
        LeadState: The updated state containing loan metrics and approval chance.
    """
    income = state.get("income_mentioned") or 0.0
    existing_emi = state.get("existing_emi") or 0.0
    property_value = state.get("property_value") or 0.0
    credit_score = state.get("credit_score") or 0
    budget = state.get("budget") or 0.0

    if income > 0:
        foir = (existing_emi / income) * 100
    else:
        foir = 0.0
    state["foir_percentage"] = foir

    if property_value > 0:
        ltv = (budget / property_value) * 100
    else:
        ltv = 0.0
    state["ltv_percentage"] = ltv

    approval = 90
    if credit_score < 600:
        approval -= 40
    if foir > 50:
        approval -= 20
    if ltv > 80:
        approval -= 20
    
    state["approval_chance"] = max(0, approval)
    
    state["eligible_loan_amount"] = income * 60
    state["estimated_emi"] = state.get("eligible_loan_amount", 0) * 0.015
    state["interest_range"] = "8.5% - 10.5%"
    state["loan_tenure_years"] = 15

    return state
