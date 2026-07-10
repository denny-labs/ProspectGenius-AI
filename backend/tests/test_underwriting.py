from app.agents.nodes.underwriting import calculate_eligibility

def test_underwriting_foir_ltv():
    state = {
        "income_mentioned": 10000,
        "existing_emi": 4000,
        "property_value": 200000,
        "budget": 150000,
        "credit_score": 700
    }
    
    result = calculate_eligibility(state)
    
    assert result["foir_percentage"] == 40.0
    assert result["ltv_percentage"] == 75.0
    assert result["approval_chance"] == 90

def test_underwriting_low_credit():
    state = {
        "income_mentioned": 10000,
        "existing_emi": 1000,
        "property_value": 200000,
        "budget": 100000,
        "credit_score": 550
    }
    
    result = calculate_eligibility(state)
    assert result["approval_chance"] == 50
