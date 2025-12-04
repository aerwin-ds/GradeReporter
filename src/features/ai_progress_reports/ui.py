"""
UI components for AI Progress Reports feature.
Author: Autumn Erwin
"""
import streamlit as st
from datetime import datetime
from typing import Optional
from src.features.ai_progress_reports.service import AIProgressReportService
from src.core.session import session


def show_progress_report_widget(student_id: int, course_id: Optional[int] = None):
    """
    Display an AI-generated progress report widget.

    Args:
        student_id: Student's ID
        course_id: Optional course ID. If None, shows aggregate report.
    """
    st.markdown("### 🤖 AI-Generated Progress Report")

    # Initialize service
    try:
        service = AIProgressReportService()
    except Exception as e:
        st.error(f"❌ {str(e)}")
        return

    # Generate/retrieve report
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write("Get personalized insights about performance, strengths, and next steps.")

    with col2:
        force_regenerate = st.button("🔄 Regenerate", help="Generate a fresh report")

    # Generate the report
    with st.spinner("🤖 Generating AI insights... This may take up to 30 seconds."):
        result = service.generate_progress_report(
            student_id=student_id,
            course_id=course_id,
            force_regenerate=force_regenerate
        )

    if not result['success']:
        st.error(f"❌ {result['error']}")
        return

    # Show cache status
    if result.get('from_cache'):
        st.info(f"📋 Showing cached report from: {result['generated_at']}")
    else:
        st.success("✅ Fresh report generated!")

    # Display the report in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Full Report", "💪 Strengths", "📈 Improvements", "🎯 Next Steps"])

    with tab1:
        st.markdown("#### Complete Progress Analysis")
        st.markdown(result['report_text'])

        # Export options
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            # Download as text
            st.download_button(
                label="📥 Download Report (TXT)",
                data=result['report_text'],
                file_name=f"progress_report_{student_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

        with col2:
            # Copy to clipboard (via text area)
            if st.button("📋 Copy to Clipboard"):
                st.code(result['report_text'], language=None)

    with tab2:
        st.markdown("#### 💪 What You're Doing Well")
        st.markdown(result['strengths'])

    with tab3:
        st.markdown("#### 📈 Areas for Growth")
        st.markdown(result['improvements'])

    with tab4:
        st.markdown("#### 🎯 Recommended Actions")
        st.markdown(result['next_steps'])


def show_progress_report_history(student_id: int):
    """
    Display historical progress reports for a student.

    Args:
        student_id: Student's ID
    """
    st.markdown("### 📚 Report History")

    try:
        service = AIProgressReportService()
        history = service.get_student_reports_history(student_id)

        if not history:
            st.info("No previous reports found.")
            return

        for i, report in enumerate(history):
            with st.expander(
                f"📄 {report.get('course_name', 'All Courses')} - {report['generated_at'][:10]}",
                expanded=(i == 0)  # Expand the most recent report
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**💪 Strengths:**")
                    st.write(report['strengths'])

                with col2:
                    st.markdown("**📈 Improvements:**")
                    st.write(report['improvements'])

                with col3:
                    st.markdown("**🎯 Next Steps:**")
                    st.write(report['next_steps'])

    except Exception as e:
        st.error(f"❌ Error loading history: {str(e)}")


def show_parent_progress_view(student_id: int, key: str = None):
    """
    Parent-friendly view of student's AI progress report.

    Args:
        student_id: Student's ID
        key: Optional Streamlit key for component uniqueness when rendering multiple children
    """
    st.markdown("### 📊 Your Child's Progress Report")

    try:
        service = AIProgressReportService()

        # Get student info for context
        from src.features.ai_progress_reports.repository import AIProgressReportRepository
        repo = AIProgressReportRepository()

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write("View AI-generated insights about your child's academic progress.")

        with col2:
            if st.button("🔄 Refresh", key=f"{key}_refresh" if key else None):
                st.rerun()

        # Generate report
        with st.spinner("Generating insights..."):
            result = service.generate_progress_report(student_id=student_id)

        if not result['success']:
            st.info(result['error'])
            return

        # Parent-friendly summary box
        st.markdown("#### 📌 Quick Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            if 'performance_data' in result:
                avg = result['performance_data']['current_average']
                st.metric("Current Average", f"{avg:.1f}%")

        with col2:
            if 'performance_data' in result:
                trend = result['performance_data']['trend_description']
                trend_emoji = "📈" if "improving" in trend else "📊" if "stable" in trend else "📉"
                st.metric("Trend", trend_emoji)

        with col3:
            if 'performance_data' in result:
                comparison = result['performance_data']['performance_compared_to_class']
                st.metric("Class Comparison", comparison.split()[1] if len(comparison.split()) > 1 else "average")

        st.markdown("---")

        # Detailed sections
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💪 Strengths")
            st.success(result['strengths'])

            st.markdown("#### 📈 Areas to Focus On")
            st.warning(result['improvements'])

        with col2:
            st.markdown("#### 🎯 How to Help")
            st.info(result['next_steps'])

        # Action buttons for parents
        st.markdown("---")
        st.markdown("#### 👥 Take Action")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📧 Request Teacher Meeting", key=f"{key}_request_meeting" if key else "request_meeting"):
                st.info("Meeting request feature coming soon!")

        with col2:
            st.download_button(
                label="📥 Download Report",
                data=result['report_text'],
                file_name=f"student_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key=f"{key}_download" if key else "download"
            )

        with col3:
            if st.button("📚 View History", key=f"{key}_view_history" if key else "view_history"):
                show_progress_report_history(student_id)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
