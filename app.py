"""
Main Streamlit application entry point for GradeReporter.
"""
import streamlit as st
from src.core.session import session
from src.ui.components.navigation import render_navigation, get_pages_for_role, get_current_page
from config.settings import APP_NAME


# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application entry point."""
    # Initialize session
    session.init_session()

    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .feature-card {
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
            margin: 1rem 0;
            background-color: #f9f9f9;
        }
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if user is logged in
    if not session.is_logged_in():
        # Show login page
        from src.ui.pages.login import show_login_page
        show_login_page()
    else:
        # Show navigation and main content
        render_navigation()

        current_page = get_current_page()

        if current_page == "home":
            from src.ui.pages.home import show_home_page
            show_home_page()

        elif current_page == "after_hours":
            from src.ui.pages.after_hours import show_after_hours_page
            show_after_hours_page()


if __name__ == "__main__":
    main()
