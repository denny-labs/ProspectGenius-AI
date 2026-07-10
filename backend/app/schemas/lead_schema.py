from pydantic import BaseModel
from typing import Optional

class UpdateLeadRequest(BaseModel):
    lead_id: str
    rm_owner: str
    customer_name: Optional[str] = None
    city: Optional[str] = None
    dob: Optional[str] = None
    income_mentioned: Optional[float] = None
    employer: Optional[str] = None
    loan_type: Optional[str] = None
    budget: Optional[float] = None
    property_value: Optional[float] = None
    existing_emi: Optional[float] = None
    credit_score: Optional[int] = None
