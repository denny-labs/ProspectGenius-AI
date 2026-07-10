"""
API Client for Backend Communication.

Handles all HTTP requests from the Streamlit frontend to the FastAPI backend.
"""
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

class APIClient:
    """Static client class for making API requests to the backend endpoints."""
    
    @staticmethod
    def get_active_leads(rm_owner: str):
        resp = requests.get(f"{API_URL}/leads/active-leads", params={"rm_owner": rm_owner})
        if resp.status_code == 200:
            return resp.json()
        return {"status": "error", "leads": []}

    @staticmethod
    def upload_document_bytes(rm_owner: str, filename: str, file_bytes: bytes):
        files = {"file": (filename, file_bytes)}
        resp = requests.post(f"{API_URL}/leads/upload", params={"rm_owner": rm_owner}, files=files)
        if resp.status_code == 200:
            return resp.json()
        return {"status": "error"}

    @staticmethod
    def update_info(payload: dict):
        resp = requests.post(f"{API_URL}/leads/update-info", json=payload)
        if resp.status_code == 200:
            return resp.json()
        return {"status": "error"}

    @staticmethod
    def recalculate(payload: dict):
        resp = requests.post(f"{API_URL}/leads/recalculate", json=payload)
        if resp.status_code == 200:
            return resp.json()
        return {"status": "error"}

    @staticmethod
    def generate_draft(payload: dict):
        resp = requests.post(f"{API_URL}/leads/generate-draft", json=payload)
        if resp.status_code == 200:
            return resp.json()
        return {"status": "error"}

