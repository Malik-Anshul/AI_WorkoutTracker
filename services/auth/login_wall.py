import streamlit as st
from services.persistence.exercise_repository import get_or_create_user

def render_login_wall():
    if st.session_state.get("user_id") is not None:
        st.header(f"Hello {st.session_state.get('username')}'s AI")
        return True
    
    
    
    st.title("🏋️ AI Real-Time GYM Trainer")
    st.markdown("### Welcome! Please enter a username to start")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Name", placeholder="Enter uniquename")
        submit_button = st.form_submit_button("start_session", width="stretch")

    if submit_button:
        if username.strip():
            user = get_or_create_user(username)
            st.session_state["username"] = user["username"]
            st.session_state["user_id"] = user["id"]
            st.rerun()
        else:
            st.error("⚠️ Please enter a username")

    return False