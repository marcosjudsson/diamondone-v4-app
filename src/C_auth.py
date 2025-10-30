# src/C_auth.py

import streamlit as st

def check_authentication():
    """
    Verifica se o usuário está autenticado na session_state.
    Se não estiver, exibe uma mensagem de erro e para a execução da página.
    """
    if not st.session_state.get('authentication_status', False):
        st.error("Acesso negado. Por favor, faça o login na página principal.")
        st.stop()
