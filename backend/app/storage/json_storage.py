"""
Local JSON Session Storage.

Manages data persistence by storing each Relationship Manager's leads in
a dedicated JSON file under the sessions/ directory.
"""
import json
import os
from typing import Dict, List, Optional, Any

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "../../data/sessions")

def _get_file_path(rm_owner: str) -> str:
    # Safely sanitize RM name
    safe_name = "".join(c for c in rm_owner if c.isalnum() or c in ('_', '-'))
    if not safe_name:
        safe_name = "default"
    return os.path.join(STORAGE_DIR, f"{safe_name}.json")

def _load_data(rm_owner: str) -> List[Dict[str, Any]]:
    """Loads all leads for a specific RM from their JSON session file."""
    path = _get_file_path(rm_owner)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def _save_data(rm_owner: str, leads: List[Dict[str, Any]]) -> None:
    """Saves a list of leads to the RM's JSON session file."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    path = _get_file_path(rm_owner)
    with open(path, "w") as f:
        json.dump(leads, f, indent=2)

def save_lead(lead_state: Dict[str, Any]) -> None:
    """
    Inserts or updates a single lead in the RM's session file.
    
    Args:
        lead_state (Dict[str, Any]): The lead state dictionary containing 'rm_owner' and 'lead_id'.
    """
    rm_owner = lead_state.get("rm_owner")
    if not rm_owner:
        return
        
    leads = _load_data(rm_owner)
    lead_id = lead_state.get("lead_id")
    
    # Update if exists, else append
    for i, lead in enumerate(leads):
        if lead.get("lead_id") == lead_id:
            leads[i] = lead_state
            _save_data(rm_owner, leads)
            return
            
    leads.append(lead_state)
    _save_data(rm_owner, leads)

def get_lead(rm_owner: str, lead_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single lead by ID for a specific RM."""
    leads = _load_data(rm_owner)
    for lead in leads:
        if lead.get("lead_id") == lead_id:
            return lead
    return None

def get_leads_by_rm(rm_owner: str) -> List[Dict[str, Any]]:
    """Retrieves all leads associated with a specific RM."""
    return _load_data(rm_owner)
