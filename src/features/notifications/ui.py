"""Streamlit UI for displaying notifications."""
import streamlit as st
from src.features.notifications.service import NotificationsService
from src.core.session import session


def show_notifications_widget():
    """Display notifications widget in sidebar or main area."""
    service = NotificationsService()
    user = session.get_current_user()

    if not user:
        return

    user_id = user.get('user_id')
    if not user_id:
        return

    # Get unread notifications
    unread_notifications = service.get_unread_notifications(user_id)

    if unread_notifications:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📬 Notifications")

        for notification in unread_notifications:
            with st.sidebar.container():
                col1, col2 = st.sidebar.columns([0.85, 0.15])

                with col1:
                    st.sidebar.info(notification['message'])

                with col2:
                    if st.sidebar.button("✓", key=f"notify_{notification['notification_id']}"):
                        service.mark_as_read(notification['notification_id'])
                        st.rerun()

        # Mark all as read button
        if st.sidebar.button("Mark all as read"):
            service.mark_all_as_read(user_id)
            st.rerun()


def show_notifications_page():
    """Render a full notifications page."""
    service = NotificationsService()
    user = session.get_current_user()

    if not user:
        st.warning("Please log in to view notifications.")
        return

    user_id = user.get('user_id')
    if not user_id:
        st.warning("User ID not found.")
        return

    st.title("📬 Notifications")

    # Get all notifications
    all_notifications = service.get_all_notifications(user_id, limit=100)

    if not all_notifications:
        st.info("No notifications yet.")
        return

    # Display notifications
    for notification in all_notifications:
        with st.container():
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])

            with col1:
                status = "✓ Read" if notification['is_read'] else "⚪ Unread"
                st.write(f"**{status}** - {notification['created_at']}")
                st.info(notification['message'])

            with col2:
                if not notification['is_read']:
                    if st.button("Mark Read", key=f"mark_{notification['notification_id']}"):
                        service.mark_as_read(notification['notification_id'])
                        st.rerun()

            with col3:
                st.write("")

        st.markdown("---")
