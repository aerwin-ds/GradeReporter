"""
Login page for the application.
"""
import streamlit as st
from src.features.authentication.service import AuthenticationService
from src.core.session import session


def show_login_page():
    """Render the login page."""
    st.markdown('<h1 class="main-header">📚 GradeReporter</h1>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Login to Your Account")

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    auth_service = AuthenticationService()
                    user_data = auth_service.authenticate(email, password)

                    if user_data:
                        session.login(user_data)
                        st.success(f"Welcome back, {user_data['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again.")

        # Demo credentials info
        with st.expander("Demo Credentials"):
            st.markdown("""
            **For Development/Testing:**

            - Student: `student@example.com` / `password`
            - Parent: `parent@example.com` / `password`
            - Teacher: `teacher@example.com` / `password`
            - Admin: `admin@example.com` / `password`

            *Note: These are placeholder credentials. Update with actual demo data.*
            """)
