import os
import time
import random
import datetime
import string
import base64
import smtplib
import socket
import json
import requests
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Google API Subsystem Verification
try:
    from google.oauth2.credentials import Credentials as GoogleCredentials
    from google_auth_oauthlib.flow import InstalledAppFlow as GoogleFlow
    from googleapiclient.discovery import build as google_build
    from google.auth.transport.requests import Request as GoogleRequest
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Page Framework Configuration
st.set_page_config(
    page_title="Enterprise Communications Dispatch Core v5.0",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Multi-Session Persistent Storage Matrix
if "master_uid" not in st.session_state:
    st.session_state.master_uid = "admin"
if "master_pwd" not in st.session_state:
    st.session_state.master_pwd = "1234"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "smtp_pool" not in st.session_state:
    st.session_state.smtp_pool = {}  
if "gmail_api_pool" not in st.session_state:
    st.session_state.gmail_api_pool = {}
if "loaded_emails" not in st.session_state:
    st.session_state.loaded_emails = []
if "sent_count" not in st.session_state:
    st.session_state.sent_count = 0
if "failed_count" not in st.session_state:
    st.session_state.failed_count = 0
if "is_sending" not in st.session_state:
    st.session_state.is_sending = False
if "global_logs" not in st.session_state:
    st.session_state.global_logs = ""

# ---------------- Master Login Layer ----------------
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>🔐 ENTERPRISE INSTANCE ACTIVATION</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c2:
        with st.form("Gate Lock"):
            in_uid = st.text_input("Master Operator ID", value=st.session_state.master_uid)
            in_pwd = st.text_input("Instance Security Key", value=st.session_state.master_pwd, type="password")
            if st.form_submit_button("Ignite Global Micro-Services Matrix"):
                if in_uid == st.session_state.master_uid and in_pwd == st.session_state.master_pwd:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Authentication Layer Rejected Instance Key.")
    st.stop()

# Sidebar Setup
st.sidebar.title("⚡ Delivery Core v5.0")
st.sidebar.markdown(f"**Dispatched Vector:** `{st.session_state.sent_count}`")
st.sidebar.markdown(f"**Failed Pipeline:** `{st.session_state.failed_count}`")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Control Tower Navigation",
    [
        "🏠 Master Campaign Engine", 
        "📂 Account & Target Lead Matrix", 
        "🛡️ IP Blacklist Network Alerts", 
        "⚙️ Core Automation Security Panel"
    ]
)

# ---------------- TAB 1: MASTER CAMPAIGN ENGINE ----------------
if menu == "🏠 Master Campaign Engine":
    st.title("🚀 Outbound Message Dispatch Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        engine_mode = st.selectbox("Outbound Target Protocol Gateway", ["Standard SMTP Matrix Engine", "Gmail API Engine (OAuth2)"])
        delivery_mode = st.selectbox("Payload Transport Interface Strategy", ["Inline Pure HTML Code", "Standard PDF Attachment"])
    with col2:
        delay_min = st.number_input("System Throttle Delay Minimum (Seconds)", value=3.0, step=0.5)
        delay_max = st.number_input("System Throttle Delay Maximum (Seconds)", value=6.0, step=0.5)

    with st.container(border=True):
        st.subheader("📝 Message Payload Formulation")
        subject_input = st.text_input("Subject Template String (Use `{ID}` for custom placeholder interpolation)", value="Notification Update Ref #{ID}")
        
        st.markdown("**HTML Structure Template / Plain Text Payload Area**")
        html_code = st.text_area(
            "Live Integrated HTML Coding Workspace", 
            value="<html><body><h2>Corporate Update</h2><p>This is an automated transmission message record reference code: <b>{ID}</b></p></body></html>", 
            height=220
        )

    # Master Action Trigger Control Button
    if not st.session_state.is_sending:
        if st.button("🚀 IGNITE ACTIVE OUTBOUND DISPATCH INTERFACE", type="primary", use_container_width=True):
            if engine_mode == "Standard SMTP Matrix Engine" and not st.session_state.smtp_pool:
                st.error("❌ Operation Aborted: Outbound SMTP routing pool empty.")
            elif engine_mode == "Gmail API Engine (OAuth2)" and not st.session_state.gmail_api_pool:
                st.error("❌ Operation Aborted: Google Cloud OAuth tokens array empty.")
            elif not st.session_state.loaded_emails:
                st.error("❌ Operation Aborted: Targeted lead list empty.")
            else:
                st.session_state.is_sending = True
                st.rerun()
    else:
        if st.button("🛑 SYSTEM CRITICAL BRAKE: TERMINATE DISPATCH FLOW", type="secondary", use_container_width=True):
            st.session_state.is_sending = False
            st.rerun()

    if st.session_state.is_sending:
        st.markdown("### 📊 In-Flight Pipeline Output Logs")
        log_feed = st.empty()
        
        smtp_list = list(st.session_state.smtp_pool.keys())
        gmail_api_list = list(st.session_state.gmail_api_pool.keys())

        for idx, recipient in enumerate(st.session_state.loaded_emails):
            if not st.session_state.is_sending:
                break
                
            rand_token = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
            live_sub = subject_input.replace("{ID}", rand_token)
            processed_html = html_code.replace("{ID}", rand_token)
            
            msg = MIMEMultipart()
            msg['To'] = recipient
            msg['Subject'] = live_sub
            
            if delivery_mode == "Inline Pure HTML Code":
                msg.attach(MIMEText(processed_html, 'html'))
            else:
                msg.attach(MIMEText(f"Please find the transmission log attached. Ref Code: {rand_token}", 'plain'))
                pdf_part = MIMEBase('application', 'octet-stream')
                pdf_part.set_payload(processed_html.encode('utf-8'))
                encoders.encode_base64(pdf_part)
                pdf_part.add_header('Content-Disposition', f'attachment; filename="Statement_{rand_token}.pdf"')
                msg.attach(pdf_part)
                
            # ---------------- PROTOCOL GATEWAY 1: GMAIL API (OAUTH2) ----------------
            if engine_mode == "Gmail API Engine (OAuth2)":
                current_api_node = gmail_api_list[idx % len(gmail_api_list)]
                try:
                    creds = GoogleCredentials.from_authorized_user_info(st.session_state.gmail_api_pool[current_api_node])
                    if creds.expired and creds.refresh_token:
                        creds.refresh(GoogleRequest())
                    service = google_build('gmail', 'v1', credentials=creds)
                    raw_payload = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                    service.users().messages().send(userId='me', body={'raw': raw_payload}).execute()
                    st.session_state.sent_count += 1
                    st.session_state.global_logs += f"[{time.strftime('%H:%M:%S')}] 🟢 [API SUCCESS] Sender {current_api_node} -> Target: {recipient} (ID: {rand_token})\n"
                except Exception as ex:
                    st.session_state.failed_count += 1
                    st.session_state.global_logs += f"[{time.strftime('%H:%M:%S')}] ❌ [API CRASH] Node {current_api_node} failed -> {recipient}: {str(ex)}\n"

            # ---------------- PROTOCOL GATEWAY 2: STANDARD SMTP NODES ----------------
            else:
                current_smtp_node = smtp_list[idx % len(smtp_list)]
                smtp_config = st.session_state.smtp_pool[current_smtp_node]
                try:
                    with smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=12) as server:
                        server.starttls()
                        server.login(current_smtp_node, smtp_config["pass"])
                        server.sendmail(current_smtp_node, recipient, msg.as_string())
                    st.session_state.sent_count += 1
                    st.session_state.global_logs += f"[{time.strftime('%H:%M:%S')}] 🟢 [SMTP SUCCESS] Matrix Node {current_smtp_node} -> Target: {recipient}\n"
                except Exception as ex:
                    st.session_state.failed_count += 1
                    st.session_state.global_logs += f"[{time.strftime('%H:%M:%S')}] ⚠️ [SMTP REFUSED] Channel {current_smtp_node} failed -> {recipient}: {str(ex)}\n"
                    
            log_feed.code(st.session_state.global_logs)
            time.sleep(random.uniform(delay_min, delay_max))
            
        st.session_state.is_sending = False
        st.rerun()

    if st.session_state.global_logs:
        st.code(st.session_state.global_logs)

# ---------------- TAB 2: ACCOUNT & TARGET LEAD MATRIX ----------------
elif menu == "📂 Account & Target Lead Matrix":
    st.title("📂 Multi-Channel Pipeline Configuration Storage Matrix")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔒 Multi-Protocol Authentication Nodes Matrix")
        
        # SMTP Loader
        with st.expander("➕ Register SMTP Routing Node (Gmail, Outlook, custom hosts)", expanded=True):
            smtp_user = st.text_input("SMTP Authorized Email Address")
