"""
Academic Calendar & Scheduling Components - Simplified Working Version
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Optional, List
import calendar as cal
from services.db import (
    get_session, AcademicYear, Term, CalendarEvent, Class, Subject, Teacher
)
from sqlmodel import select, desc, asc
from utils.rbac import get_current_user, has_permission


def render_academic_calendar():
    """Main academic calendar interface"""
    st.title("📅 Academic Calendar & Scheduling")
    
    user = get_current_user()
    if not user:
        st.error("Please log in to access this feature.")
        return
    
    # Create simplified tabs based on user role
    if user['role'] in ['Head', 'Admin']:
        tab1, tab2, tab3 = st.tabs([
            "📅 Calendar View", 
            "🗓️ Academic Years", 
            "📋 Events"
        ])
        
        with tab1:
            render_calendar_view()
        
        with tab2:
            render_academic_year_management()
        
        with tab3:
            render_event_management()
    else:
        tab1, tab2 = st.tabs([
            "📅 Calendar View", 
            "⏰ My Schedule"
        ])
        
        with tab1:
            render_calendar_view()
        
        with tab2:
            render_teacher_schedule()


def render_calendar_view():
    """Render basic calendar view"""
    st.header("📅 Calendar View")
    
    # Get current academic year info
    with get_session() as session:
        current_year = session.exec(
            select(AcademicYear).where(AcademicYear.is_current == True)
        ).first()
        
        if current_year:
            current_term = session.exec(
                select(Term).where(
                    Term.academic_year_id == current_year.id,
                    Term.is_current == True
                )
            ).first()
            
            st.info(f"**Current Academic Year:** {current_year.year} | **Current Term:** {current_term.name if current_term else 'No active term'}")
        else:
            st.warning("No current academic year set. Please set up academic years first.")
    
    # Date selector
    selected_date_raw = st.date_input("Select Date", value=date.today())
    
    # Handle Streamlit date input return type
    if isinstance(selected_date_raw, tuple):
        selected_date = selected_date_raw[0] if selected_date_raw else date.today()
    else:
        selected_date = selected_date_raw or date.today()
    
    # Show basic calendar view
    st.subheader(f"Calendar for {selected_date.strftime('%B %d, %Y')}")
    
    # Get events for selected date
    events = get_events_for_date(selected_date)
    
    if events:
        st.subheader("📅 Events")
        for event in events:
            with st.container():
                st.markdown(f"**{event.title}**")
                if event.description:
                    st.write(event.description)
                time_str = "All Day" if event.is_all_day else event.start_date.strftime('%H:%M')
                st.caption(f"Time: {time_str}")
                st.divider()
    else:
        st.info("No events for this date.")


def render_academic_year_management():
    """Simplified academic year management"""
    st.header("🗓️ Academic Years Management")
    
    user = get_current_user()
    if not user:
        st.error("Access denied")
        return
    
    # Display existing academic years
    with get_session() as session:
        academic_years = session.exec(
            select(AcademicYear).order_by(desc(AcademicYear.start_date))
        ).all()
        
        if academic_years:
            st.subheader("Existing Academic Years")
            for year in academic_years:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    status = "🟢 Current" if year.is_current else ""
                    st.write(f"**{year.year}** {status}")
                    st.write(f"{year.start_date.strftime('%Y-%m-%d')} to {year.end_date.strftime('%Y-%m-%d')}")
                
                with col2:
                    if not year.is_current and st.button(f"Set Current", key=f"set_current_{year.id}"):
                        set_current_academic_year(year.id or 0)
                        st.rerun()
                
                with col3:
                    if st.button(f"Delete", key=f"delete_{year.id}"):
                        delete_academic_year(year.id or 0)
                        st.rerun()
        else:
            st.info("No academic years found.")
    
    # Add new academic year
    st.subheader("Add New Academic Year")
    with st.form("add_academic_year"):
        year_name = st.text_input("Academic Year (e.g., 2024-2025)")
        col1, col2 = st.columns(2)
        with col1:
            start_date_raw = st.date_input("Start Date")
        with col2:
            end_date_raw = st.date_input("End Date")
        
        description = st.text_area("Description (Optional)")
        is_current = st.checkbox("Set as Current Year")
        
        if st.form_submit_button("Add Academic Year"):
            if year_name and start_date_raw and end_date_raw:
                # Handle Streamlit date input types
                start_date = start_date_raw[0] if isinstance(start_date_raw, tuple) and start_date_raw else start_date_raw
                end_date = end_date_raw[0] if isinstance(end_date_raw, tuple) and end_date_raw else end_date_raw
                
                create_academic_year(year_name, start_date, end_date, description, is_current)
                st.success("Academic year created successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields.")


def render_event_management():
    """Simplified event management"""
    st.header("📋 Events Management")
    
    user = get_current_user()
    if not user:
        st.error("Access denied")
        return
    
    # Show upcoming events
    st.subheader("Upcoming Events")
    upcoming_events = get_upcoming_events()
    
    if upcoming_events:
        for event in upcoming_events[:10]:  # Show first 10
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{event.title}**")
                    st.write(f"📅 {event.start_date.strftime('%Y-%m-%d')}")
                    if event.description:
                        st.caption(event.description)
                with col2:
                    if st.button("Delete", key=f"del_event_{event.id}"):
                        delete_event(event.id or 0)
                        st.rerun()
                st.divider()
    else:
        st.info("No upcoming events.")
    
    # Add new event
    st.subheader("Add New Event")
    with st.form("add_event"):
        title = st.text_input("Event Title")
        description = st.text_area("Description (Optional)")
        event_type = st.selectbox("Event Type", [
            "Holiday", "Exam", "Meeting", "Deadline", "Other"
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            event_date_raw = st.date_input("Date")
        with col2:
            is_all_day = st.checkbox("All Day Event", value=True)
        
        start_time = None
        end_time = None
        if not is_all_day:
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")
        
        if st.form_submit_button("Add Event"):
            if title and event_date_raw and event_type:
                # Handle Streamlit date input types
                event_date = event_date_raw[0] if isinstance(event_date_raw, tuple) and event_date_raw else event_date_raw
                
                # Convert time objects to strings if needed
                start_time_str = start_time.strftime("%H:%M:%S") if start_time else None
                end_time_str = end_time.strftime("%H:%M:%S") if end_time else None
                
                create_calendar_event(
                    title, description or "", event_type, event_date, 
                    start_time_str if not is_all_day else None, 
                    event_date, end_time_str if not is_all_day else None,
                    is_all_day, user['id']
                )
                st.success("Event created successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields.")


def render_teacher_schedule():
    """Teacher schedule view"""
    st.header("⏰ My Schedule")
    
    user = get_current_user()
    if not user:
        st.error("Access denied")
        return
    
    st.info("Teacher schedule view - Coming soon!")
    
    # Show teacher's events
    events = get_upcoming_events()
    if events:
        st.subheader("My Upcoming Events")
        for event in events[:5]:
            with st.container():
                st.markdown(f"**{event.title}**")
                st.write(f"📅 {event.start_date.strftime('%Y-%m-%d %H:%M')}")
                if event.description:
                    st.caption(event.description)
                st.divider()


# Helper functions
def get_events_for_date(selected_date: date) -> List[CalendarEvent]:
    """Get events for a specific date"""
    with get_session() as session:
        start_datetime = datetime.combine(selected_date, datetime.min.time())
        end_datetime = datetime.combine(selected_date, datetime.max.time())
        
        events = session.exec(
            select(CalendarEvent).where(
                CalendarEvent.start_date >= start_datetime,
                CalendarEvent.start_date <= end_datetime
            )
        ).all()
        
        return list(events)


def get_upcoming_events(days_ahead: int = 30) -> List[CalendarEvent]:
    """Get upcoming events"""
    with get_session() as session:
        end_date = datetime.now() + timedelta(days=days_ahead)
        
        events = session.exec(
            select(CalendarEvent).where(
                CalendarEvent.start_date >= datetime.now(),
                CalendarEvent.start_date <= end_date
            ).order_by(asc(CalendarEvent.start_date))
        ).all()
        
        return list(events)


def create_academic_year(year: str, start_date: date, end_date: date, 
                        description: Optional[str], is_current: bool):
    """Create new academic year"""
    with get_session() as session:
        # If setting as current, unset all others first
        if is_current:
            for existing_year in session.exec(select(AcademicYear)).all():
                existing_year.is_current = False
                session.add(existing_year)
        
        new_year = AcademicYear(
            year=year,
            start_date=datetime.combine(start_date, datetime.min.time()),
            end_date=datetime.combine(end_date, datetime.min.time()),
            is_current=is_current,
            description=description
        )
        
        session.add(new_year)
        session.commit()


def create_calendar_event(title: str, description: str, event_type: str, 
                         start_date: date, start_time: Optional[str],
                         end_date: date, end_time: Optional[str],
                         is_all_day: bool, created_by: int):
    """Create new calendar event"""
    from datetime import time as dt_time
    
    with get_session() as session:
        if is_all_day:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else start_datetime
        else:
            # Parse time strings back to time objects
            if start_time:
                hour, minute, second = map(int, start_time.split(':'))
                start_time_obj = dt_time(hour, minute, second)
            else:
                start_time_obj = datetime.min.time()
            
            if end_time:
                hour, minute, second = map(int, end_time.split(':'))
                end_time_obj = dt_time(hour, minute, second)
            else:
                end_time_obj = start_time_obj
            
            start_datetime = datetime.combine(start_date, start_time_obj)
            end_datetime = datetime.combine(end_date, end_time_obj) if end_date else start_datetime
        
        event = CalendarEvent(
            title=title,
            description=description,
            event_type=event_type,
            start_date=start_datetime,
            end_date=end_datetime,
            is_all_day=is_all_day,
            created_by=created_by
        )
        
        session.add(event)
        session.commit()


def set_current_academic_year(year_id: int):
    """Set academic year as current"""
    with get_session() as session:
        # Unset all current years
        for year in session.exec(select(AcademicYear)).all():
            year.is_current = False
            session.add(year)
        
        # Set the selected year as current
        year = session.get(AcademicYear, year_id)
        if year:
            year.is_current = True
            session.add(year)
            session.commit()


def delete_academic_year(year_id: int):
    """Delete academic year"""
    with get_session() as session:
        year = session.get(AcademicYear, year_id)
        if year:
            session.delete(year)
            session.commit()


def delete_event(event_id: int):
    """Delete calendar event"""
    with get_session() as session:
        event = session.get(CalendarEvent, event_id)
        if event:
            session.delete(event)
            session.commit()