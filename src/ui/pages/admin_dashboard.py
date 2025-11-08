"""
Admin dashboard page.
"""
import streamlit as st
from src.core.decorators import require_role


@require_role('admin')
def show_admin_dashboard():
    """Render the admin dashboard."""
    st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)

    # Placeholder content
    st.info("🚧 Admin dashboard under construction. Will display system statistics and management tools.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Students", "0", help="Total number of students")

    with col2:
        st.metric("Total Teachers", "0", help="Total number of teachers")

    with col3:
        st.metric("Total Courses", "0", help="Total number of courses")

    st.markdown("### ⚙️ System Management")
    st.write("User management, course management, and system settings will appear here...")
