import streamlit as st
from src.core.decorators import require_role
from src.core.session import session
from src.features.feature_8.service import LowGradeAlertService

alert_service = LowGradeAlertService()

def show_alert_card(alert: dict, dismissible: bool = False, student_id: int = None):
    with st.container(border=True):
        col1, col2 = st.columns([0.85, 0.15])

        with col1:
            alert_type = alert['alert_type'].replace('_', ' ').title()
            grade_text = f" ({alert['current_grade']:.1f}%)" if alert.get('current_grade') else ""
            st.markdown(f"**{alert_type}** in {alert['course_name']}{grade_text}")
            st.markdown(alert['alert_message'])

        with col2:
            if dismissible and student_id:
                if st.button("Dismiss", key=f"dismiss_{alert['alert_id']}", use_container_width=True):
                    result = alert_service.dismiss_alert(alert['alert_id'], student_id)
                    if result['success']:
                        st.success("Dismissed")
                        st.rerun()
                    else:
                        st.error(result['message'])

@require_role("student")
def show_student_alerts_page():
    user = session.get_current_user()
    student_id = user.get("student_id")

    st.markdown("<h1>Grade Alerts & Improvement Tips</h1>", unsafe_allow_html=True)

    alerts = alert_service.get_student_alerts(student_id)

    if not alerts:
        st.success("Great job! No low grade alerts at this time. Keep up the good work!")
        return

    st.warning(f"You have {len(alerts)} alert(s) that need your attention")
    st.markdown("---")

    for alert in alerts:
        show_alert_card(alert, dismissible=True, student_id=student_id)
        st.markdown("")

@require_role("parent")
def show_parent_alerts_page():
    user = session.get_current_user()
    parent_id = user.get("parent_id")

    st.markdown("<h1>Your Children's Grade Alerts</h1>", unsafe_allow_html=True)

    from config.database import db_manager

    query = """
        SELECT s.student_id, u.name
        FROM Students s
        JOIN Users u ON s.user_id = u.user_id
        JOIN Parent_Student ps ON s.student_id = ps.student_id
        WHERE ps.parent_id = ?
        ORDER BY u.name
    """
    children = db_manager.execute_query(query, (parent_id,))

    if not children:
        st.info("No children linked to your account.")
        return

    children_dict = {name: sid for sid, name in children}
    selected_child = st.selectbox("Select Child", list(children_dict.keys()))
    selected_child_id = children_dict[selected_child]

    st.markdown("---")

    alerts = alert_service.repository.get_parent_student_alerts(
        parent_id, selected_child_id, dismissed=False
    )

    if not alerts:
        st.success(f"Great news! {selected_child} has no low grade alerts.")
    else:
        st.warning(f"{selected_child} has {len(alerts)} alert(s)")
        st.markdown("")

        for alert in alerts:
            show_alert_card(alert)
            st.markdown("")

    st.markdown("---")
    st.markdown("### How You Can Help")
    guidance = alert_service.get_parent_guidance(selected_child_id)
    st.info(guidance)

@require_role("teacher")
def show_teacher_at_risk_students():
    user = session.get_current_user()
    teacher_id = user.get("teacher_id")

    st.markdown("<h1>Students Needing Attention</h1>", unsafe_allow_html=True)

    at_risk = alert_service.get_teacher_at_risk_students(teacher_id)

    if not at_risk:
        st.success("All your students are doing well!")
        return

    st.warning(f"You have {len(at_risk)} student(s) with active grade alerts")
    st.markdown("---")

    from config.database import db_manager

    for student_info in at_risk:
        student_id = student_info[0]
        student_name = student_info[1]

        with st.expander(f"**{student_name}** - At Risk", expanded=True):
            student_alerts = alert_service.get_student_alerts(student_id)

            for alert in student_alerts:
                st.markdown(f"**{alert['alert_type'].replace('_', ' ').title()}** - {alert['course_name']}")
                st.markdown(alert['alert_message'])
                st.markdown("---")

            if st.button("Contact This Student's Parent", key=f"contact_{student_id}"):
                st.info("You can contact parents through the 'Contact Teachers' feature (Parent Engagement)")
