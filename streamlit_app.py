"""
AI Banking Assistant - Streamlit Frontend Application
"""

import os
import requests
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Banking Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .badge-source {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
    }
    .stChatMessage {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_url = st.text_input(
        "API Base URL",
        value="http://localhost:8085/api/v1",
        help="URL du serveur backend FastAPI/Flask",
    )
    
    # Predefined Customer IDs
    customer_options = {
        "C1024 - Marc Dupont": "C1024",
        "C1025 - Sophie Martin": "C1025",
        "C1026 - Thomas Bernard": "C1026",
        "C1027 - Julie Petit": "C1027",
        "C1028 - Antoine Richard": "C1028",
    }
    
    selected_customer_label = st.selectbox(
        "Sélectionner un Client",
        options=list(customer_options.keys()),
        index=0,
    )
    customer_id = customer_options[selected_customer_label]

    st.markdown("---")
    
    # Server Health Check
    st.subheader("📡 Statut du Serveur")
    health_url = f"{api_url.rstrip('/api/v1')}/health"
    try:
        health_res = requests.get(health_url, timeout=2)
        if health_res.status_code == 200:
            st.success("Connecté (200 OK)")
        else:
            st.warning(f"Réponse: {health_res.status_code}")
    except Exception:
        st.error("Serveur indisponible")

    st.markdown("---")
    
    # Quick Prompts / Examples
    st.subheader("💡 Exemples de questions")
    
    sample_queries = [
        ("💰 Solde disponible", "Quel est mon solde ?"),
        ("💳 Statut de carte", "Quel est le statut de ma carte ?"),
        ("📜 Historique opérations", "Quels sont mes derniers paiements ?"),
        ("🔄 Virement refusé (Tool+RAG)", "Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?"),
        ("✈️ Frais virement (RAG)", "Quels sont les frais pour un virement international ?"),
        ("🚨 Perte de carte (RAG)", "Que faire en cas de perte de carte ?"),
    ]
    
    for label, prompt in sample_queries:
        if st.button(label, use_container_width=True):
            st.session_state.selected_prompt = prompt

    st.markdown("---")
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Layout ---
st.markdown('<div class="main-title">🏦 Assistant Bancaire IA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Posez vos questions sur vos comptes, virements ou procédures bancaires.</div>', unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "source" in msg:
            st.markdown(f'<span class="badge-source">Source : {msg["source"]}</span>', unsafe_allow_html=True)
        if "documents" in msg and msg["documents"]:
            with st.expander("📄 Documents de référence (RAG)"):
                for doc in msg["documents"]:
                    st.write(f"- `{doc}`")

# Process Prompt (from chat_input or quick prompt button)
user_prompt = st.chat_input("Posez votre question bancaire ici...")

if st.session_state.selected_prompt:
    user_prompt = st.session_state.selected_prompt
    st.session_state.selected_prompt = None

if user_prompt:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Call Chat Backend API
    chat_endpoint = f"{api_url}/chat"
    payload = {"customer_id": customer_id, "message": user_prompt}

    with st.chat_message("assistant"):
        with st.spinner("Analyse et génération de la réponse..."):
            try:
                response = requests.post(chat_endpoint, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Aucune réponse reçue.")
                    source = data.get("source", "inconnu")
                    docs = data.get("documents", [])

                    st.markdown(answer)
                    st.markdown(f'<span class="badge-source">Source : {source}</span>', unsafe_allow_html=True)

                    if docs:
                        with st.expander("📄 Documents de référence (RAG)"):
                            for doc in docs:
                                st.write(f"- `{doc}`")

                    # Store in session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "source": source,
                        "documents": docs,
                    })
                else:
                    error_msg = f"❌ Erreur Serveur ({response.status_code}) : {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"⚠️ Impossible de contacter le serveur : {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
