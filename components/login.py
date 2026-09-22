"""Password gate backed only by the APP_PASSWORD environment variable."""

import hmac
import os

import streamlit as st


def require_password():
    """Stop the app until the visitor enters the configured password."""
    expected = os.environ.get("APP_PASSWORD")
    if not expected:
        st.error("APP_PASSWORD is not configured. The application is locked.")
        st.stop()

    if st.session_state.get("_password_authenticated", False):
        return

    def check_password():
        entered = st.session_state.get("_password_input", "")
        if hmac.compare_digest(entered, expected):
            st.session_state["_password_authenticated"] = True
            st.session_state["_password_error"] = False
            st.session_state.pop("_password_input", None)
        else:
            st.session_state["_password_error"] = True

    st.title("Vransko jezero · 2025")
    st.caption("Enter the application password to open the viewer.")
    st.text_input(
        "Password",
        type="password",
        key="_password_input",
        on_change=check_password,
    )
    if st.session_state.get("_password_error", False):
        st.error("Incorrect password.")
    st.stop()
