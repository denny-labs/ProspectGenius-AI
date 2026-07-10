"""
Leads API Endpoints.

Handles CRUD operations, file uploads (CSV, Numbers, Excel), and LLM draft generation.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Any, Dict
import uuid
from app.agents.graph import graph
from app.agents.state import LeadState
from app.storage import json_storage
from app.schemas.lead_schema import UpdateLeadRequest
from app.api.v1.endpoints.file_parsers import extract_text_from_bytes, extract_tabular_data_from_bytes

router = APIRouter()

@router.post("/upload")
async def upload_document(rm_owner: str, file: UploadFile = File(...)) -> Any:
    """
    Endpoint for uploading lead data files (TXT, PDF, CSV, Excel, Numbers).
    Parses the file, extracts leads, runs them through the LangGraph AI workflow,
    and saves them to the RM's session.
    """
    content = await file.read()
    ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    if ext in ['numbers', 'xlsx', 'xls', 'csv']:
        print(f"\\n---> [BULK IMPORT START] Detected tabular file: {file.filename}")
        rows = extract_tabular_data_from_bytes(file.filename, content)
        print(f"---> [BULK IMPORT PARSE] Successfully extracted {len(rows)} rows from the file")
        
        if not rows:
            print("---> [BULK IMPORT ERROR] No rows found or parsing failed!")
            raise HTTPException(status_code=400, detail="Could not extract data from tabular file")
            
        print("---> [BULK IMPORT SAVE] Mapping columns and saving to database...")
        for idx, row in enumerate(rows):
            if idx == 0:
                print(f"---> [BULK IMPORT PREVIEW] First row Customer Name: {row.get('Customer_Name')}")
            lead_id = str(uuid.uuid4())
            def safe_float(val):
                try:
                    return float(str(val).replace(',', ''))
                except:
                    return 0.0

            missing_docs = row.get("Missing_Documents", "")
            missing_list = [d.strip() for d in missing_docs.split(",")] if missing_docs else []

            initial_state: LeadState = {
                "lead_id": lead_id,
                "rm_owner": rm_owner,
                "raw_context": f"Imported from {file.filename}",
                "customer_name": row.get("Customer_Name", ""),
                "city": row.get("City", ""),
                "dob": None,
                "income_mentioned": safe_float(row.get("Monthly_Income")),
                "employer": row.get("Occupation", ""),
                "loan_type": row.get("Loan_Type", ""),
                "budget": safe_float(row.get("Loan_Amount_Req")),
                "property_value": safe_float(row.get("Property_Value")),
                "missing_fields": missing_list,
                "risk_level": "Low" if safe_float(row.get("Lead_Score")) > 70 else "Medium",
                "primary_product": row.get("Product_Fit", ""),
                "secondary_products": [],
                "lead_score": int(safe_float(row.get("Lead_Score"))),
                "buying_intent": row.get("Priority", ""),
                "urgency": row.get("Priority", ""),
                "ai_20_sec_summary": row.get("AI_Summary", ""),
                "rm_whatsapp_draft": row.get("RM_Action", ""),
                "rm_action_plan": row.get("RM_Action", ""),
                "is_profile_complete": len(missing_list) == 0,
                "rm_phone_script": None,
                "credit_score": safe_float(row.get("Credit_Score")) if row.get("Credit_Score") else 750,
                "existing_emi": safe_float(row.get("Existing_EMI")),
                "document_verification_logs": {},
                "is_docs_valid": len(missing_list) == 0,
            }
            
            from app.agents.nodes.underwriting import calculate_eligibility
            initial_state = calculate_eligibility(initial_state)
            
            json_storage.save_lead(initial_state)
            
        return {"status": "success", "message": f"Successfully imported {len(rows)} leads."}
    
    else:
        raw_text = extract_text_from_bytes(file.filename, content)
        
        lead_id = str(uuid.uuid4())
        initial_state: LeadState = {
            "lead_id": lead_id,
            "rm_owner": rm_owner,
            "raw_context": raw_text,
            "customer_name": None,
            "city": None,
            "dob": None,
            "income_mentioned": None,
            "employer": None,
            "loan_type": None,
            "budget": None,
            "property_value": None,
            "missing_fields": [],
            "risk_level": None,
            "primary_product": None,
            "secondary_products": [],
            "lead_score": None,
            "buying_intent": None,
            "urgency": None,
            "ai_20_sec_summary": None,
            "rm_whatsapp_draft": None,
            "rm_action_plan": None,
            "is_profile_complete": False,
            "rm_phone_script": None,
            "credit_score": None,
            "existing_emi": None,
            "document_verification_logs": {},
            "is_docs_valid": False,
            "eligible_loan_amount": None,
            "estimated_emi": None,
            "interest_range": None,
            "loan_tenure_years": None,
            "foir_percentage": None,
            "ltv_percentage": None,
            "approval_chance": None
        }
        
        try:
            final_state = graph.invoke(initial_state)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
        json_storage.save_lead(final_state)
        
        return {"status": "success", "lead_id": lead_id, "state": final_state}

@router.get("/active-leads")
async def get_active_leads(rm_owner: str) -> Any:
    """
    Retrieves all active leads belonging to the specified RM.
    """
    leads = json_storage.get_leads_by_rm(rm_owner)
    return {"status": "success", "leads": leads}

@router.post("/update-info")
async def update_info(payload: UpdateLeadRequest) -> Any:
    lead = json_storage.get_lead(payload.rm_owner, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    update_data = payload.dict(exclude_unset=True)
    for k, v in update_data.items():
        if v is not None:
            lead[k] = v
            
    json_storage.save_lead(lead)
    return {"status": "success", "state": lead}

@router.post("/recalculate")
async def recalculate(payload: Dict[str, Any]) -> Any:
    rm_owner = payload.get("rm_owner")
    lead_id = payload.get("lead_id")
    lead = json_storage.get_lead(rm_owner, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    from app.agents.nodes.doc_intel import verify_documents
    from app.agents.nodes.underwriting import calculate_eligibility
    from app.agents.nodes.auditor import validate_fields
    
    lead = validate_fields(lead)
    lead = verify_documents(lead)
    lead = calculate_eligibility(lead)
    
    json_storage.save_lead(lead)
    return {"status": "success", "state": lead}

@router.post("/generate-draft")
async def generate_draft(payload: Dict[str, Any]) -> Any:
    """
    Triggers the AI Outreach agent to dynamically generate a personalized 
    WhatsApp, Email, or SMS draft for a specific lead based on a chosen tone.
    """
    rm_owner = payload.get("rm_owner")
    lead_id = payload.get("lead_id")
    lead = json_storage.get_lead(rm_owner, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead["draft_channel"] = payload.get("channel", "WhatsApp")
    lead["draft_tone"] = payload.get("tone", "Professional")
        
    from app.agents.nodes.outreach import generate_outreach
    lead = generate_outreach(lead)
    
    json_storage.save_lead(lead)
    return {"status": "success", "state": lead}
