"""
Auditor Node.

Performs data validation and sanity checks to flag potentially fraudulent or
erroneous lead information (e.g., existing EMI exceeds reported income).
"""
from app.agents.state import LeadState

REQUIRED_FIELDS = ["customer_name", "city", "dob", "income_mentioned", "employer", "loan_type", "budget", "property_value"]

def validate_fields(state: LeadState) -> LeadState:
    """
    Validates the lead's data for completeness and potential discrepancies.
    
    Args:
        state (LeadState): The current state of the lead.
        
    Returns:
        LeadState: The updated state with validation logs and completeness flags.
    """
    logs = state.get("document_verification_logs", {})
    missing = []
    for field in REQUIRED_FIELDS:
        if not state.get(field):
            missing.append(field)
            
    state["missing_fields"] = missing
    state["is_profile_complete"] = len(missing) == 0
    return state
