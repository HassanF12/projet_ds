from pathlib import Path
import sys

# 1. Résolution du chemin racine
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from src.rag.assistant import RagAssistant

st.set_page_config(
    page_title="Electric Skate Assistant",
    page_icon="🛹",
)

st.title("🛹 Electric Skate Assistant")
st.caption("Posez vos questions sur les modèles, vitesses, poids et autonomies.")


# 2. Chargement de l'assistant en cache unique
@st.cache_resource
def get_assistant() -> RagAssistant:
    return RagAssistant()


assistant = get_assistant()

# 3. Initialisation de l'historique des messages dans la session
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Affichage de l'ensemble des messages déjà échangés
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Zone de saisie utilisateur en bas de page
if user_input := st.chat_input("Votre message..."):
    # A. Afficher et mémoriser le message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # B. Générer, afficher et mémoriser la réponse de l'assistant
    with st.chat_message("assistant"):
        with st.spinner("Recherche dans les spécifications..."):
            response = assistant.query(user_input)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})