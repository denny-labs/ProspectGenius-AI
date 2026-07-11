"""
Streamlit Frontend Application.

This module provides the interactive dashboard for Relationship Managers (RMs)
to upload, view, and process banking leads using the LangGraph AI backend.
"""
import streamlit as st
from api_client import APIClient
import uuid

st.set_page_config(page_title="Antigravity Banking Suite", layout="wide", initial_sidebar_state="collapsed")

# --- CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(88, 166, 255, 0.3);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #58a6ff;
        margin-top: 5px;
    }
    .metric-label {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .badge {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIN GATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>BANKING SUITE - ENTERPRISE SECURITY PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center; letter-spacing: 2px;'>ENTERPRISE SIGN IN</h3>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            
            username = st.text_input("Relationship Manager Username", placeholder="e.g. prabu")
            password = st.text_input("Security Access Key Token", type="password", placeholder="*************")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("AUTHENTICATE SIGN IN", use_container_width=True):
                if username and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Access Denied. Invalid token.")
    st.stop()

rm_owner = st.session_state.username

# --- DATA FETCHING ---
active_leads_resp = APIClient.get_active_leads(rm_owner)
leads = active_leads_resp.get("leads", [])

# --- MAIN LAYOUT (3 COLUMNS) ---
col1, col2, col3 = st.columns([1.2, 2.0, 1.2])

# ================= COLUMN 1 =================
with col1:
    c_prof1, c_prof2 = st.columns([2, 1])
    with c_prof1:
        st.markdown(f"<div style='font-size: 16px; font-weight: bold; margin-top: 5px;'>👔 RM Dashboard | 👤 {rm_owner}</div>", unsafe_allow_html=True)
    with c_prof2:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
            
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 10px 0;'>", unsafe_allow_html=True)
    st.markdown("### 📥 USER DIRECTORY")
    
    if leads:
        df_leads = []
        for l in leads:
            score = l.get("lead_score", 0)
            df_leads.append({
                "Lead ID": l.get("lead_id")[:6].upper(),
                "Name": l.get("customer_name", "Unknown"),
                "Score": score if isinstance(score, int) else 0,
                "_full_id": l.get("lead_id")
            })
            
        # Streamlit Native Interactive Directory (No PyArrow)
        
        if "lead_filter" not in st.session_state:
            st.session_state.lead_filter = "all"
            
        current_filter = st.session_state.lead_filter
        filter_text = ""
        if current_filter == "hot":
            filter_text = " <span style='color:#ef4444;'>[HOT LEADS]</span>"
        elif current_filter == "pending":
            filter_text = " <span style='color:#fbbf24;'>[PENDING REVIEW]</span>"

        st.markdown(f"<div style='font-size:12px; color:#8b949e; margin-bottom: 10px; font-weight:bold; letter-spacing:1px;'>LEAD DIRECTORY{filter_text}</div>", unsafe_allow_html=True)
        
        with st.container(height=300):
            # Header Row
            h1, h2, h3, h4 = st.columns([1.5, 2, 1, 1])
            h1.markdown("**Lead ID**")
            h2.markdown("**Name**")
            h3.markdown("**Score**")
            st.markdown("<hr style='margin:0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            
            # Data Rows
            for l in df_leads:
                # Apply the filter logic
                if current_filter == "hot" and l['Score'] <= 80:
                    continue
                if current_filter == "pending" and l['Score'] > 80:
                    continue
                    
                r1, r2, r3, r4 = st.columns([1.5, 2, 1, 1])
                r1.markdown(f"`{l['Lead ID']}`")
                r2.markdown(f"<span style='font-size:14px;'>{l['Name']}</span>", unsafe_allow_html=True)
                
                # Color code the score
                score_color = "#58a6ff"
                if l['Score'] > 80:
                    score_color = "#ef4444"
                elif l['Score'] < 50:
                    score_color = "#fbbf24"
                    
                r3.markdown(f"<span style='color:{score_color}; font-weight:bold;'>{l['Score']}</span>", unsafe_allow_html=True)
                if r4.button("►", key=f"btn_{l['_full_id']}", help="View Details"):
                    st.session_state.selected_lead_id = l['_full_id']
                    st.rerun()
                st.markdown("<hr style='margin:0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 ANALYTICS SUMMARY")
        hot_leads = sum(1 for l in leads if (l.get("lead_score") or 0) > 80)
        pending_leads = len(leads) - hot_leads
        
        st.markdown("<div style='font-size: 11px; color: #8b949e; margin-bottom: 5px;'>CLICK TO FILTER:</div>", unsafe_allow_html=True)
        
        if st.button(f"Total Leads: {len(leads)}", use_container_width=True):
            st.session_state.lead_filter = "all"
            st.rerun()
            
        if st.button(f"Hot Leads (>80): {hot_leads}", use_container_width=True):
            st.session_state.lead_filter = "hot"
            st.rerun()
            
        if st.button(f"Pending Review: {pending_leads}", use_container_width=True):
            st.session_state.lead_filter = "pending"
            st.rerun()

    else:
        st.info("No leads available in your directory.")
        st.session_state.selected_lead_id = None

lead_data = None
if st.session_state.get("selected_lead_id"):
    lead_data = next((l for l in leads if l["lead_id"] == st.session_state.selected_lead_id), None)


# ================= COLUMN 2 =================
with col2:
    c2_title, c2_upload = st.columns([2, 1])
    with c2_title:
        st.markdown("### 🎯 CENTRAL WORKSPACE")
    with c2_upload:
        with st.popover("📤 Upload Data", use_container_width=True):
            uploaded_file = st.file_uploader("Upload", type=["txt", "csv", "docx", "doc", "xlsx", "xls", "pdf", "numbers", "pages"], label_visibility="collapsed")
            if uploaded_file is not None:
                if st.button("Process", use_container_width=True):
                    with st.spinner("Processing..."):
                        resp = APIClient.upload_document_bytes(rm_owner, uploaded_file.name, uploaded_file.getvalue())
                        st.success("Uploaded!")
                        st.rerun()

    if not lead_data:
        st.markdown("<div class='glass-card'>Please select a lead from the directory to view details.</div>", unsafe_allow_html=True)
    else:
        is_hot = (lead_data.get("lead_score") or 0) > 80
        badge_html = "<span class='badge'>🔥 HOT LEAD</span>" if is_hot else ""
        
        st.markdown(f"**Lead Details** | ID: {lead_data['lead_id'][:8].upper()} {badge_html}", unsafe_allow_html=True)
        
        # Profile Card
        st.markdown(f"""
        <div class='glass-card'>
            <div style='display: flex; gap: 20px; align-items: center;'>
                <div style='background: #1f2937; height: 60px; width: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px;'>👤</div>
                <div>
                    <h2 style='margin: 0; font-size: 22px;'>{lead_data.get('customer_name') or 'Unknown Client'}</h2>
                    <div style='color: #8b949e; font-size: 14px;'>📍 {lead_data.get('city') or 'Unknown City'}</div>
                </div>
            </div>
            <hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                <div><span style='color: #8b949e; font-weight:600;'>Emp:</span> {lead_data.get('employer') or 'N/A'}</div>
                <div><span style='color: #8b949e; font-weight:600;'>Income:</span> ₹{lead_data.get('income_mentioned') or '0'} /mo</div>
                <div><span style='color: #8b949e; font-weight:600;'>Type:</span> {lead_data.get('loan_type') or 'N/A'}</div>
                <div><span style='color: #8b949e; font-weight:600;'>Budget:</span> ₹{lead_data.get('budget') or '0'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Summary
        st.markdown(f"""
        <div class='glass-card'>
            <div class='metric-label'>🤖 AI 20-SECOND SUMMARY</div>
            <p style='margin-top: 10px; font-size: 14px; line-height: 1.6; color: #c9d1d9;'>
                {lead_data.get('ai_20_sec_summary') or 'No summary available.'}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Split Checklists
        c2a, c2b = st.columns(2)
        with c2a:
            checklist_html = "<div class='glass-card' style='height: 100%;'>"
            checklist_html += "<div class='metric-label'>📑 DOCUMENT CHECKLIST</div><div style='margin-top: 15px;'>"
            missing = lead_data.get("missing_fields", [])
            all_reqs = ["PAN Card", "Aadhaar", "Salary Slip", "Bank Statement"]
            for req in all_reqs:
                is_missing = any(req.lower()[:3] in m.lower() for m in missing)
                if is_missing or (req == "Salary Slip" and any("income" in m.lower() for m in missing)):
                    checklist_html += f"<div style='margin-bottom:8px;'>✘ {req} <span style='color: #ef4444; font-size: 11px; float: right; font-weight:bold;'>[MISSING]</span></div>"
                else:
                    checklist_html += f"<div style='margin-bottom:8px;'>✔ {req} <span style='color: #10b981; font-size: 11px; float: right; font-weight:bold;'>[DONE]</span></div>"
            checklist_html += "</div></div>"
            st.markdown(checklist_html, unsafe_allow_html=True)
            
        with c2b:
            elig_html = "<div class='glass-card' style='height: 100%;'>"
            elig_html += "<div class='metric-label'>💰 ELIGIBILITY ESTIMATE</div>"
            elig_html += f"""
            <div style='margin-top: 15px;'>
                <div style='margin-bottom:12px; font-size: 14px;'>Eligible:<br><strong style='color:#58a6ff; font-size: 20px;'>₹{lead_data.get('eligible_loan_amount') or 0:,.2f}</strong></div>
                <div style='margin-bottom:12px; font-size: 14px;'>Est. EMI:<br><strong style='color:#58a6ff; font-size: 18px;'>₹{lead_data.get('estimated_emi') or 0:,.2f}/mo</strong></div>
                <div style='margin-bottom:8px; font-size: 14px;'>Approval:<br><strong style='color:#10b981; font-size: 18px;'>94%</strong></div>
            </div>
            </div>
            """
            st.markdown(elig_html, unsafe_allow_html=True)


# ================= COLUMN 3 =================
with col3:
    st.markdown("### ⚡ ACTION PANEL")
    
    if not lead_data:
        st.info("Select a lead to view actions.")
    else:
        tab1, tab2 = st.tabs(["AI Drafts", "RM Notes"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            ch_col, tone_col, gen_col = st.columns([1, 1, 1.2])
            with ch_col:
                channel = st.selectbox("Channel", ["WhatsApp", "Email", "SMS"])
            with tone_col:
                tone = st.selectbox("Tone", ["Professional", "Casual", "Urgent"])
            with gen_col:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("✨ Auto-Draft", use_container_width=True):
                    with st.spinner("AI drafting..."):
                        APIClient.generate_draft({
                            "rm_owner": rm_owner, 
                            "lead_id": lead_data["lead_id"],
                            "channel": channel,
                            "tone": tone
                        })
                        st.rerun()
                
            draft_content = lead_data.get("rm_whatsapp_draft") or ""
            st.text_area("Draft Editor", value=draft_content, height=250, label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                st.button("Save", use_container_width=True)
            with b2:
                st.button("Send", type="primary", use_container_width=True)
            
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.text_area("RM Internal Notes", height=300, placeholder="Add notes here...")
            st.button("Save Notes", use_container_width=True)
