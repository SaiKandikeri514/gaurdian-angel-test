import streamlit as st
from agent import SecurityOrchestrator
import difflib
import json

st.set_page_config(page_title="Guardian Angel", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .stTextArea textarea {
        background-color: #262730;
        color: #ffffff;
    }
    .stTextArea textarea::placeholder {
        color: #ffffff;
        opacity: 0.7;
    }
    .stTextArea textarea:focus::placeholder {
        color: transparent;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        height: 3em;
    }
    h1 {
        color: #ff4b4b;
    }
    .vuln-card {
        background-color: #ffffff;
        color: #333333;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-title {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# Logo and Title
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    # st.image("assets/cross_me_logo.png", width=150) # Assuming logo is saved here, using placeholder for now
    st.markdown("<h1 class='main-title'>🛡️ Guardian Angel</h1>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center'>
    <h3>🚀 Automate your code reviews.</h3>
    <p>Paste your code below. The agent will <strong>detect vulnerabilities</strong> and <strong>propose secure fixes</strong>.</p>
</div>
""", unsafe_allow_html=True)

# Initialize Orchestrator
if 'agent' not in st.session_state:
    try:
        st.session_state.agent = SecurityOrchestrator()
        st.toast("Security Orchestrator Ready", icon="🤖")
    except Exception as e:
        st.error(f"Error initializing orchestrator: {e}. Please check your .env file and API Key.")

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Simulated Pull Request")
    code_input = st.text_area("Paste code snippet here:", height=300, value="", placeholder="Enter your code here")

analyze_button = st.button("🔍 Analyze & Fix Vulnerabilities")

# ... (Previous code)

if analyze_button and code_input:
    if 'agent' in st.session_state:
        with st.spinner("🕵️‍♂️ Analyzing code for vulnerabilities..."):
            try:
                # 1. Analyze
                analysis_json_str = st.session_state.agent.analyze_code(code_input)
                
                # Parse JSON
                try:
                    analysis_data = json.loads(analysis_json_str)
                except json.JSONDecodeError:
                    st.error("Failed to parse agent output. Raw output:")
                    st.code(analysis_json_str)
                    st.stop()

                # 2. Fix
                fixed_code = st.session_state.agent.fix_code(code_input, analysis_json_str)
                
                # Store results in session state
                st.session_state.analysis_data = analysis_data
                st.session_state.fixed_code = fixed_code
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

# Results Section
if 'analysis_data' in st.session_state:
    st.divider()
    
    data = st.session_state.analysis_data
    risk_score = data.get("risk_score", 100)
    vulnerabilities = data.get("vulnerabilities", [])
    summary = data.get("summary", "Analysis complete.")

    # 📊 Metrics Dashboard
    st.subheader("📊 Security Insights")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Risk Score", f"{risk_score}/100", delta=risk_score-100 if risk_score < 100 else 0)
        st.caption(data.get("risk_score_deviation", ""))
    with m2:
        st.metric("Vulnerabilities Found", len(vulnerabilities), delta=-len(vulnerabilities), delta_color="inverse")
    with m3:
        if risk_score == 100:
             st.metric("Status", "Secure", delta="Pass", delta_color="normal")
        else:
             st.metric("Status", "At Risk", delta="Fail", delta_color="inverse")

    # 🚨 Detailed Report
    st.subheader("🚨 Detected Vulnerabilities")
    st.info(summary)
    
    if not vulnerabilities:
        st.success("✅ No vulnerabilities detected! Good job.")
    else:
        # Display vulnerabilities in a grid layout
        for i, vuln in enumerate(vulnerabilities):
            severity_color = "#ff4b4b" if vuln['severity'] == "High" else "#ff8c00" if vuln['severity'] == "Medium" else "#0068c9"
            severity_icon = "🔴" if vuln['severity'] == "High" else "🟠" if vuln['severity'] == "Medium" else "🔵"
            
            st.markdown(f"""
            <div class="vuln-card" style="
                background: linear-gradient(to right, {severity_color}15 0%, white 5%);
                border-left: 6px solid {severity_color};
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 15px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h3 style="margin: 0; color: #333; font-size: 1.2em;">
                        {severity_icon} {vuln['type']}
                    </h3>
                    <span style="
                        background-color: {severity_color};
                        color: white;
                        padding: 6px 16px;
                        border-radius: 20px;
                        font-weight: 600;
                        font-size: 0.85em;
                    ">{vuln['severity']}</span>
                </div>
                
                <div style="margin: 15px 0;">
                    <div style="display: inline-block; background-color: #f0f2f6; padding: 6px 12px; border-radius: 6px; margin-bottom: 10px;">
                        <strong style="color: #555;">📍 Line:</strong> 
                        <code style="background-color: #e8eaf0; padding: 2px 6px; border-radius: 3px; color: #333;">{vuln.get('line', '?')}</code>
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 3px solid {severity_color};">
                    <p style="margin: 0; color: #444; line-height: 1.6;">
                        <strong style="color: #222;">Description:</strong><br/>
                        {vuln['description']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    # Code Comparison
    st.subheader("✅ Secure Implementation")
    
    col_vuln, col_fix = st.columns(2)
    
    with col_vuln:
        st.markdown("### ❌ Vulnerable Code")
        st.code(code_input, language='python')
        
    with col_fix:
        st.markdown("### 🛡️ Fixed Code")
        st.code(st.session_state.fixed_code, language='python')

    # Diff View
    with st.expander("Show Detailed Diff"):
        diff = difflib.unified_diff(
            code_input.splitlines(),
            st.session_state.fixed_code.splitlines(),
            fromfile='Original',
            tofile='Fixed',
            lineterm=''
        )
        diff_text = "\n".join(list(diff))
        st.code(diff_text, language='diff')

    st.divider()
    st.subheader("🏁 Decision")
    
    col_accept, col_reject = st.columns(2)
    
    with col_accept:
        if st.button("✅ Accept Fix", key="btn_accept", help="Apply this fix to the codebase"):
            st.success("Fix accepted! Code has been updated (Simulated).")
            st.code(st.session_state.fixed_code, language='python')
            st.balloons()
            
    with col_reject:
        if st.button("❌ Reject Fix", key="btn_reject", help="Discard this fix"):
            st.warning("Fix rejected. You can modify the input code and analyze again.")
            # Optional: Clear state to force re-analysis if needed, but keeping it visible is often better for comparison.
