"""
LangGraph State Schema.

Defines the LeadState TypedDict which represents the central state object
passed and mutated between the LangGraph AI nodes.
"""
from typing import TypedDict, Optional, List, Dict, Any

class LeadState(TypedDict):
    lead_id: str
    rm_owner: str
    customer_name: Optional[str]
    city: Optional[str]
    purpose: Optional[str]
    loan_type: Optional[str]
    budget: Optional[float]
    preferred_contact: Optional[str]
    timeline: Optional[str]
    income_mentioned: Optional[float]
    employer: Optional[str]
    property_value: Optional[float]
    existing_customer: Optional[bool]
    customer_type: Optional[str]
    lead_score: Optional[int]
    buying_intent: Optional[str]
    urgency: Optional[str]
    risk_level: Optional[str]
    primary_product: Optional[str]
    secondary_products: List[str]
    ai_20_sec_summary: Optional[str]
    missing_fields: List[str]
    is_profile_complete: bool
    rm_phone_script: Optional[str]
    rm_whatsapp_draft: Optional[str]
    dob: Optional[str]
    credit_score: Optional[int]
    existing_emi: Optional[float]
    document_verification_logs: Dict[str, Any]
    is_docs_valid: bool
    eligible_loan_amount: Optional[float]
    estimated_emi: Optional[float]
    interest_range: Optional[str]
    loan_tenure_years: Optional[int]
    foir_percentage: Optional[float]
    ltv_percentage: Optional[float]
    approval_chance: Optional[int]
