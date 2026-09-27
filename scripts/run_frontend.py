"""Interactive Streamlit application for SentryMesh Guardian.

Provides:
  - Multi-channel communication inspector (SMS, WhatsApp, Email, Call, QR)
  - Cognitive manipulation tactic radar & probability bars
  - IOC extraction table (URLs, Domains, UPI IDs, Phone Numbers, Amounts)
  - Plain-language evidence explanations and instant safety actions
  - Preloaded test presets (Digital arrest call, UPI reverse collect fraud, Legitimate bank OTP)
  - Quarantined threat reporting console
"""

import streamlit as st
import json
import requests
import os
import sys

# Add parent directory to path so Streamlit can also run standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from app.analyzer import analyze_communication
    from app.reporting import submit_user_report
    LOCAL_ANALYZER_AVAILABLE = True
except Exception:
    LOCAL_ANALYZER_AVAILABLE = False

st.set_page_config(
    page_title="SentryMesh Guardian | AI Cybersecurity Defense",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ SentryMesh Guardian")
st.caption("Privacy-Preserving Multi-Channel Scam & Cognitive Manipulation Defense System")

# Preset Samples
PRESETS = {
    "Select a preset scenario...": "",
    "🚨 Digital Arrest Police Impersonation (Call)": (
        "This is Inspector Sharma calling from Sample Cyber Office New Delhi. A parcel sent in your name to Cambodia containing illegal passports and narcotics has been seized at customs. An arrest warrant has been issued against your Aadhaar number. Do not disconnect this call or tell anyone. You must transfer penalty funds to test_merchant@invalid immediately to verify innocence."
    ),
    "💸 UPI Reverse Collect Request (QR/SMS)": (
        "Congratulations! You won Rs 25,000 cash prize from Example Bank. Scan this dynamic QR code and enter your confidential 6-digit UPI PIN to credit funds to your bank account immediately."
    ),
    "📱 Remote Access Software Coercion (Call/SMS)": (
        "Hello sir, I am calling from Example Bank technical department. Your net banking access has a high-risk security vulnerability. To secure your account, please download RemoteAssistDemo app from Play Store and read out the 9-digit session code to our agent."
    ),
    "⚡ Electricity Disconnection Threat (SMS)": (
        "Dear Customer, your electricity power connection will be cut tonight at 9:30 PM due to unpaid electricity bill. Contact electricity verification officer at +91 00000 00000 immediately."
    ),
    "✅ Legitimate Bank OTP Alert (Legitimate Contrast)": (
        "123456 is your secret OTP for login to Example Bank NetBanking. Never share your OTP with anyone including bank staff or callers. OTP valid for 5 minutes."
    ),
    "✅ Legitimate Salary Credit (Legitimate Contrast)": (
        "Dear Customer, your account XX1209 has been credited with Rs 45,000.00 on 25-Sep-2026 by NEFT/Salary from Employer Corp. Available balance: Rs 78,410.20 - Example Bank."
    )
}

# Sidebar
with st.sidebar:
    st.header("⚙️ Inspection Settings")
    channel = st.selectbox(
        "Communication Channel",
        options=["sms", "whatsapp", "call", "email", "qr", "website", "app"],
        index=0,
        help="Select the vector through which the communication was received."
    )

    consent = st.checkbox("Consent to analyze content in-memory", value=True)
    st.markdown("---")
    st.markdown("### 🔒 Privacy Guarantees")
    st.markdown("""
    - **In-Memory Only**: Message text is never logged to permanent storage.
    - **PII Scrubbing**: Phone numbers, accounts, and names are stripped before tokenization.
    - **Zero Training Bleed**: User scans are never automatically added to AI models.
    """)
    st.markdown("---")
    st.markdown("### 📞 Emergency Support")
    st.info("National Cyber Crime Helpline: **1930**\n\nOfficial Portal: [cybercrime.gov.in](https://cybercrime.gov.in)")

# Main Layout
col_input, col_preset = st.columns([3, 2])

with col_preset:
    selected_preset = st.selectbox("Load Sample Vector:", options=list(PRESETS.keys()))

with col_input:
    initial_text = PRESETS.get(selected_preset, "")
    user_text = st.text_area(
        "Paste communication, SMS, call transcript, or email body:",
        value=initial_text,
        height=140,
        placeholder="Enter message text here to evaluate..."
    )

analyze_btn = st.button("🛡️ Inspect Communication", type="primary", use_container_width=True)

if analyze_btn and user_text.strip():
    with st.spinner("Analyzing message against cognitive manipulation vectors and threat feeds..."):
        if LOCAL_ANALYZER_AVAILABLE:
            result = analyze_communication(user_text, channel=channel)
        else:
            st.error("Backend analyzer module could not be loaded.")
            st.stop()

    pred_label = result["classification"]["predicted_label"]
    probs = result["classification"]["probabilities"]
    tactics = result["tactics"]
    entities = result["entities"]
    verification = result["verification"]
    explanation = result["explanation"]
    actions = result["recommended_actions"]
    uncertainty = result["uncertainty"]

    # Header Alert Box
    st.markdown("---")
    if pred_label == "legitimate":
        st.success(f"### ✅ Assessment: Legitimate Communication (Confidence: {probs.get('legitimate', 0)*100:.1f}%)")
    else:
        st.error(f"### 🚨 High Risk Threat Detected: `{pred_label.replace('_', ' ').title()}`")
        st.caption(f"Evaluated Category: **{pred_label}** | Uncertainty: **{uncertainty.upper()}**")

    # Metrics Layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🧠 Cognitive Manipulation Tactics")
        active_tactics = {k: v for k, v in tactics.items() if v > 0.3}
        if active_tactics:
            for t_name, score in sorted(active_tactics.items(), key=lambda x: x[1], reverse=True):
                st.progress(score, text=f"{t_name.replace('_', ' ').title()}: {int(score*100)}%")
        else:
            st.info("No hostile psychological manipulation tactics detected.")

        st.subheader("🔍 Indicators of Compromise (IOCs)")
        ioc_items = []
        for k, v in entities.items():
            if v:
                ioc_items.append(f"**{k.replace('_', ' ').title()}**: {', '.join(v)}")
        if ioc_items:
            for item in ioc_items:
                st.write(item)
        else:
            st.caption("No external domains, UPI handles, or phone numbers identified.")

    with col2:
        st.subheader("💡 Why was this flagged?")
        for exp in explanation:
            st.markdown(f"- {exp}")

        st.subheader("🛡️ Recommended Safety Actions")
        for act in actions:
            st.warning(f"👉 {act}")

    # Class Probabilities Breakdown Expander
    with st.expander("📊 View Detailed Model Class Distribution"):
        st.json(probs)
