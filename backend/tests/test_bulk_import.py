import os
from app.api.v1.endpoints.file_parsers import extract_tabular_data_from_bytes

def test_numbers_file_parsing():
    file_path = os.path.join(os.path.dirname(__file__), "sample_lead_data_120_rows.numbers")
    assert os.path.exists(file_path), "Test file not found"
    
    with open(file_path, "rb") as f:
        content = f.read()
        
    rows = extract_tabular_data_from_bytes("sample_lead_data_120_rows.numbers", content)
    
    # Assert we got the rows
    assert len(rows) > 0, "Parser returned no rows"
    
    print(f"\\nSuccessfully parsed {len(rows)} rows from the .numbers file!")
    
    # Verify mapping of the first row
    first_row = rows[0]
    print(f"First row Customer_Name: {first_row.get('Customer_Name')}")
    print(f"First row Lead_Score: {first_row.get('Lead_Score')}")
    print(f"First row RM_Owner: {first_row.get('RM_Owner')}")
    
    assert "Customer_Name" in first_row
    assert "Lead_Score" in first_row
