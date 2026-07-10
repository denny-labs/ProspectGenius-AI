from app.agents.graph import graph
from app.agents.state import LeadState

def test_incomplete_profile_routing():
    initial_state = {
        "lead_id": "test-1",
        "customer_name": None,
        "city": None,
        "is_profile_complete": False,
        "missing_fields": []
    }
    
    final_state = graph.invoke(initial_state)
    assert final_state["is_profile_complete"] == False
    assert len(final_state["missing_fields"]) > 0
    assert "rm_phone_script" in final_state

def test_complete_profile_routing():
    initial_state = {
        "lead_id": "test-2",
        "customer_name": "John Doe",
        "city": "NY",
        "dob": "1990-01-01",
        "income_mentioned": 5000,
        "employer": "Tech Corp",
        "loan_type": "Personal",
        "budget": 50000,
        "property_value": 100000,
        "is_profile_complete": False,
        "missing_fields": []
    }
    
    final_state = graph.invoke(initial_state)
    assert final_state["is_profile_complete"] == True
    assert final_state["missing_fields"] == []
    assert final_state.get("eligible_loan_amount") is not None
