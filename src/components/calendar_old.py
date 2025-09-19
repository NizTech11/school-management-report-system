"""
Academic Calendar & Scheduling Components
Handles academic years, terms, calendar events, timetables, and exam schedules
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Optional, List
import calendar
from services.db import (
    get_session, AcademicYear, Term, CalendarEvent, Timetable, 
    ExamSchedule, Class, Subject, Teacher
)
from sqlmodel import select, desc, asc
from utils.rbac import get_current_user, has_permission


def render_events_management():
    """Manage calendar events"""
    st.header("📋 Calendar Events Management")
    
    user = get_current_user()
    if not user or not has_permission(user['role'], 'calendar.create'):
from utils.rbac import get_current_user, has_permission


def render_academic_calendar():
    """Main academic calendar interface"""
    st.title("📅 Academic Calendar & Scheduling")
    
    user = get_current_user()
    if not user:
        st.error("Please log in to access this feature.")
        return
    
    # Create tabs for different calendar functions
    if user['role'] in ['Head', 'Admin']:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📅 Calendar View", 
            "🗓️ Academic Years", 
            "📋 Events", 
            "⏰ Timetables", 
            "📝 Exam Schedule"
        ])
    else:
        tab1, tab2, tab3 = st.tabs([
            "📅 Calendar View", 
            "⏰ My Timetable", 
            "📝 Exam Schedule"
        ])
    
    with tab1:
        render_calendar_view()
    
    if user['role'] in ['Head', 'Admin']:
        with tab2:
            render_academic_years_management()
        
        with tab3:
            render_events_management()
        
        with tab4:
            render_timetable_management()
        
        with tab5:
            render_exam_schedule_management()
    else:
        with tab2:
            render_teacher_timetable()
        
        with tab3:
            render_exam_schedule_view()


def render_calendar_view():
    """Render calendar view with events"""
    st.header("📅 Calendar View")
    
    # Date selector
    col1, col2 = st.columns(2)
    with col1:
        selected_date_input = st.date_input("Select Date", value=date.today())
    
    with col2:
        view_mode = st.selectbox("View Mode", ["Month", "Week", "Day"])
    
    # Ensure selected_date is a date object
    if isinstance(selected_date_input, tuple):
        selected_date = selected_date_input[0] if selected_date_input else date.today()
    else:
        selected_date = selected_date_input or date.today()
    
    # Get current academic year and term
    current_year, current_term = get_current_academic_info()
    
    if current_year:
        st.info(f"**Current Academic Year:** {current_year.year} | **Current Term:** {current_term.name if current_term else 'No active term'}")
    else:
        st.warning("No current academic year set. Please set up academic years first.")
    
    # Display calendar based on view mode
    if view_mode == "Month":
        render_month_calendar(selected_date)
    elif view_mode == "Week":
        render_week_calendar(selected_date)
    else:
        render_day_calendar(selected_date)


def render_month_calendar(selected_date: date):
    """Render month calendar view"""
    # Get events for the month
    start_of_month = selected_date.replace(day=1)
    next_month = start_of_month.replace(month=start_of_month.month % 12 + 1)
    end_of_month = next_month - timedelta(days=1)
    
    events = get_events_for_period(start_of_month, end_of_month)
    
    # Display month header
    st.subheader(f"{selected_date.strftime('%B %Y')}")
    
    # Create calendar grid
    cal = calendar.monthcalendar(selected_date.year, selected_date.month)
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Header row
    cols = st.columns(7)
    for i, day in enumerate(weekdays):
        cols[i].write(f"**{day[:3]}**")
    
    # Calendar days
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                day_date = date(selected_date.year, selected_date.month, day)
                day_events = [e for e in events if e.start_date.date() == day_date]
                
                # Highlight today
                if day_date == date.today():
                    cols[i].markdown(f"**🟦 {day}**")
                else:
                    cols[i].write(str(day))
                
                # Show events for this day
                for event in day_events[:2]:  # Show max 2 events
                    event_emoji = get_event_emoji(event.event_type)
                    cols[i].caption(f"{event_emoji} {event.title[:10]}...")
                
                if len(day_events) > 2:
                    cols[i].caption(f"+ {len(day_events) - 2} more...")
    
    # Events list for selected month
    st.markdown("---")
    st.subheader("Events This Month")
    
    if events:
        for event in sorted(events, key=lambda x: x.start_date):
            render_event_card(event)
    else:
        st.info("No events scheduled for this month.")


def render_week_calendar(selected_date: date):
    """Render week calendar view"""
    # Calculate week start (Monday)
    days_since_monday = selected_date.weekday()
    week_start = selected_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    events = get_events_for_period(week_start, week_end)
    
    st.subheader(f"Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
    
    # Create columns for each day
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    cols = st.columns(7)
    
    for i, day_name in enumerate(weekdays):
        current_day = week_start + timedelta(days=i)
        day_events = [e for e in events if e.start_date.date() == current_day]
        
        with cols[i]:
            # Header
            if current_day == date.today():
                st.markdown(f"**🟦 {day_name}**")
                st.markdown(f"**{current_day.strftime('%m/%d')}**")
            else:
                st.write(f"**{day_name}**")
                st.write(current_day.strftime('%m/%d'))
            
            # Events
            for event in day_events:
                event_emoji = get_event_emoji(event.event_type)
                time_str = event.start_date.strftime('%H:%M') if not event.is_all_day else "All Day"
                
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 5px; border-radius: 5px; margin: 2px 0;">
                        {event_emoji} <strong>{event.title}</strong><br>
                        <small>{time_str}</small>
                    </div>
                    """, unsafe_allow_html=True)


def render_day_calendar(selected_date: date):
    """Render day calendar view"""
    events = get_events_for_period(selected_date, selected_date)
    
    st.subheader(f"{selected_date.strftime('%A, %B %d, %Y')}")
    
    if selected_date == date.today():
        st.info("📍 Today")
    
    # Show timetable for the day
    timetable = get_timetable_for_day(selected_date)
    
    if timetable:
        st.markdown("### 📚 Class Schedule")
        for slot in timetable:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.write(f"**{slot.start_time} - {slot.end_time}**")
                with col2:
                    st.write(slot.subject_name)
                with col3:
                    st.write(slot.class_name)
                with col4:
                    st.write(slot.room or "TBA")
    
    # Show events for the day
    st.markdown("### 📅 Events")
    if events:
        for event in sorted(events, key=lambda x: x.start_date):
            render_event_card(event)
    else:
        st.info("No events scheduled for this day.")


def render_academic_years_management():
    """Manage academic years and terms"""
    st.header("🗓️ Academic Years Management")
    
    user = get_current_user()
    if not user or not has_permission(user['role'], 'calendar.create'):
        st.error("You don't have permission to manage academic years.")
        return
    
    # Academic Years section
    st.subheader("Academic Years")
    
    # Add new academic year
    with st.expander("➕ Add New Academic Year"):
        with st.form("add_academic_year"):
            year = st.text_input("Academic Year", placeholder="e.g., 2024-2025")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
            description = st.text_area("Description (Optional)")
            is_current = st.checkbox("Set as Current Year")
            
            if st.form_submit_button("Create Academic Year"):
                create_academic_year(year, start_date, end_date, description, is_current)
    
    # Display existing academic years
    with get_session() as session:
        academic_years = session.exec(select(AcademicYear).order_by(desc(AcademicYear.start_date))).all()
    
    if academic_years:
        for year in academic_years:
            with st.expander(f"📅 {year.year} {'(Current)' if year.is_current else ''}", expanded=year.is_current):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Period:** {year.start_date.strftime('%B %d, %Y')} - {year.end_date.strftime('%B %d, %Y')}")
                    if year.description:
                        st.write(f"**Description:** {year.description}")
                
                with col2:
                    if not year.is_current and st.button("Set as Current", key=f"current_{year.id}"):
                        set_current_academic_year(year.id)
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_year_{year.id}", type="secondary"):
                        delete_academic_year(year.id)
                        st.rerun()
                
                # Terms for this academic year
                render_terms_for_year(year)
    else:
        st.info("No academic years created yet.")


def render_terms_for_year(academic_year: AcademicYear):
    """Render terms for a specific academic year"""
    st.markdown(f"**Terms for {academic_year.year}:**")
    
    with get_session() as session:
        terms = session.exec(
            select(Term).where(Term.academic_year_id == academic_year.id).order_by(asc(Term.start_date))
        ).all()
    
    # Add new term
    with st.form(f"add_term_{academic_year.id}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            term_name = st.text_input("Term Name", placeholder="e.g., Term 1")
        with col2:
            term_start = st.date_input("Start Date", key=f"term_start_{academic_year.id}")
        with col3:
            term_end = st.date_input("End Date", key=f"term_end_{academic_year.id}")
        
        if st.form_submit_button("Add Term"):
            create_term(academic_year.id, term_name, term_start, term_end)
            st.rerun()
    
    # Display terms
    if terms:
        for term in terms:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                status = " (Current)" if term.is_current else ""
                st.write(f"**{term.name}**{status}: {term.start_date.strftime('%m/%d')} - {term.end_date.strftime('%m/%d/%Y')}")
            with col2:
                if not term.is_current and st.button("Set Current", key=f"current_term_{term.id}"):
                    set_current_term(term.id)
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"delete_term_{term.id}", type="secondary"):
                    delete_term(term.id)
                    st.rerun()
    else:
        st.info("No terms created for this academic year.")


def render_events_management():
    """Manage calendar events"""
    st.header("📋 Events Management")
    
    user = get_current_user()
    if not has_permission(user['role'], 'calendar.create'):
        st.error("You don't have permission to manage events.")
        return
    
    # Add new event
    with st.expander("➕ Add New Event"):
        with st.form("add_event"):
            title = st.text_input("Event Title")
            description = st.text_area("Description (Optional)")
            
            event_type = st.selectbox(
                "Event Type", 
                ["holiday", "exam", "meeting", "event", "deadline"],
                format_func=lambda x: x.replace("_", " ").title()
            )
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
                start_time = st.time_input("Start Time")
            
            with col2:
                end_date = st.date_input("End Date (Optional)")
                end_time = st.time_input("End Time")
            
            is_all_day = st.checkbox("All Day Event")
            
            # Optional associations
            with get_session() as session:
                classes = session.exec(select(Class)).all()
                academic_years = session.exec(select(AcademicYear)).all()
            
            col1, col2 = st.columns(2)
            with col1:
                if classes:
                    class_options = ["All Classes"] + [f"{c.name} ({c.category})" for c in classes]
                    selected_class = st.selectbox("Associate with Class (Optional)", class_options)
            
            with col2:
                if academic_years:
                    year_options = ["All Years"] + [y.year for y in academic_years]
                    selected_year = st.selectbox("Academic Year", year_options)
            
            if st.form_submit_button("Create Event"):
                create_calendar_event(
                    title, description, event_type, start_date, start_time,
                    end_date, end_time, is_all_day, selected_class, selected_year
                )
    
    # Display existing events
    st.subheader("Upcoming Events")
    upcoming_events = get_upcoming_events()
    
    if upcoming_events:
        for event in upcoming_events:
            render_event_card(event, show_actions=True)
    else:
        st.info("No upcoming events.")


def render_timetable_management():
    """Manage class timetables"""
    st.header("⏰ Timetable Management")
    
    user = get_current_user()
    if not has_permission(user['role'], 'calendar.create'):
        st.error("You don't have permission to manage timetables.")
        return
    
    # Get current academic year
    current_year, current_term = get_current_academic_info()
    if not current_year:
        st.warning("Please set up an academic year first.")
        return
    
    with get_session() as session:
        classes = session.exec(select(Class)).all()
        subjects = session.exec(select(Subject)).all()
        teachers = session.exec(select(Teacher)).all()
    
    if not all([classes, subjects]):
        st.warning("Please create classes and subjects first.")
        return
    
    # Class selection for timetable
    selected_class = st.selectbox(
        "Select Class",
        classes,
        format_func=lambda x: f"{x.name} ({x.category})"
    )
    
    if selected_class:
        render_class_timetable(selected_class, current_year, subjects, teachers)


def render_class_timetable(class_obj: Class, academic_year: AcademicYear, subjects: List[Subject], teachers: List[Teacher]):
    """Render and manage timetable for a specific class"""
    st.subheader(f"Timetable for {class_obj.name}")
    
    # Add timetable entry
    with st.expander("➕ Add Timetable Entry"):
        with st.form(f"add_timetable_{class_obj.id}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                subject = st.selectbox("Subject", subjects, format_func=lambda x: f"{x.name} ({x.code})")
                teacher = st.selectbox("Teacher", [None] + teachers, format_func=lambda x: f"{x.first_name} {x.last_name}" if x else "No Teacher")
            
            with col2:
                day_of_week = st.selectbox(
                    "Day of Week", 
                    list(range(7)),
                    format_func=lambda x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x]
                )
                room = st.text_input("Room (Optional)")
            
            with col3:
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
            
            if st.form_submit_button("Add to Timetable"):
                create_timetable_entry(
                    class_obj.id, subject.id, teacher.id if teacher else None,
                    day_of_week, start_time, end_time, room, academic_year.id
                )
                st.rerun()
    
    # Display current timetable
    display_class_timetable(class_obj.id, academic_year.id)


def render_exam_schedule_management():
    """Manage exam schedules"""
    st.header("📝 Exam Schedule Management")
    
    user = get_current_user()
    if not has_permission(user['role'], 'calendar.create'):
        st.error("You don't have permission to manage exam schedules.")
        return
    
    # Get current term
    current_year, current_term = get_current_academic_info()
    if not current_term:
        st.warning("Please set up a current term first.")
        return
    
    with get_session() as session:
        classes = session.exec(select(Class)).all()
        subjects = session.exec(select(Subject)).all()
    
    # Add exam schedule
    with st.expander("➕ Schedule New Exam"):
        with st.form("add_exam_schedule"):
            title = st.text_input("Exam Title", placeholder="e.g., Mid-Term Mathematics Exam")
            
            col1, col2 = st.columns(2)
            with col1:
                if classes:
                    class_obj = st.selectbox("Class", classes, format_func=lambda x: f"{x.name} ({x.category})")
                if subjects:
                    subject = st.selectbox("Subject", subjects, format_func=lambda x: f"{x.name} ({x.code})")
            
            with col2:
                exam_date = st.date_input("Exam Date")
                room = st.text_input("Room (Optional)")
            
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
            with col2:
                duration = st.number_input("Duration (minutes)", min_value=30, max_value=300, value=120)
            
            instructions = st.text_area("Special Instructions (Optional)")
            
            if st.form_submit_button("Schedule Exam"):
                create_exam_schedule(
                    title, subject.id, class_obj.id, exam_date, start_time, end_time,
                    room, duration, instructions, current_term.id
                )
                st.rerun()
    
    # Display exam schedules
    st.subheader("Upcoming Exams")
    upcoming_exams = get_upcoming_exams(current_term.id)
    
    if upcoming_exams:
        for exam in upcoming_exams:
            render_exam_card(exam, show_actions=True)
    else:
        st.info("No upcoming exams scheduled.")


# Helper functions
def get_event_emoji(event_type: str) -> str:
    """Get emoji for event type"""
    emoji_map = {
        'holiday': '🏖️',
        'exam': '📝',
        'meeting': '👥',
        'event': '🎉',
        'deadline': '⏰'
    }
    return emoji_map.get(event_type, '📅')


def render_event_card(event: CalendarEvent, show_actions: bool = False):
    """Render an event card"""
    emoji = get_event_emoji(event.event_type)
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if event.is_all_day:
                time_str = "All Day"
            else:
                if event.end_date:
                    time_str = f"{event.start_date.strftime('%H:%M')} - {event.end_date.strftime('%H:%M')}"
                else:
                    time_str = event.start_date.strftime('%H:%M')
            
            st.markdown(f"""
            **{emoji} {event.title}**  
            📅 {event.start_date.strftime('%B %d, %Y')} | ⏰ {time_str}  
            {event.description if event.description else ''}
            """)
        
        if show_actions:
            with col2:
                if st.button("Delete", key=f"delete_event_{event.id}", type="secondary"):
                    delete_calendar_event(event.id)
                    st.rerun()


def render_exam_card(exam: ExamSchedule, show_actions: bool = False):
    """Render an exam schedule card"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            **📝 {exam.title}**  
            📅 {exam.exam_date.strftime('%B %d, %Y')} | ⏰ {exam.start_time} - {exam.end_time}  
            🏫 Room: {exam.room or 'TBA'} | ⏱️ Duration: {exam.duration_minutes or 0} minutes  
            {f"📋 {exam.instructions}" if exam.instructions else ''}
            """)
        
        if show_actions:
            with col2:
                if st.button("Delete", key=f"delete_exam_{exam.id}", type="secondary"):
                    delete_exam_schedule(exam.id)
                    st.rerun()


# Database helper functions continue in next part...
def get_current_academic_info():
    """Get current academic year and term"""
    with get_session() as session:
        current_year = session.exec(select(AcademicYear).where(AcademicYear.is_current == True)).first()
        current_term = session.exec(select(Term).where(Term.is_current == True)).first()
    return current_year, current_term


def get_events_for_period(start_date: date, end_date: date) -> List[CalendarEvent]:
    """Get events for a specific date range"""
    with get_session() as session:
        events = session.exec(
            select(CalendarEvent).where(
                CalendarEvent.start_date >= datetime.combine(start_date, datetime.min.time()),
                CalendarEvent.start_date <= datetime.combine(end_date, datetime.max.time())
            ).order_by(CalendarEvent.start_date)
        ).all()
    return events


def create_academic_year(year: str, start_date: date, end_date: date, description: str, is_current: bool):
    """Create new academic year"""
    with get_session() as session:
        # If setting as current, unset other current years
        if is_current:
            current_years = session.exec(select(AcademicYear).where(AcademicYear.is_current == True)).all()
            for cy in current_years:
                cy.is_current = False
                session.add(cy)
        
        new_year = AcademicYear(
            year=year,
            start_date=datetime.combine(start_date, datetime.min.time()),
            end_date=datetime.combine(end_date, datetime.max.time()),
            is_current=is_current,
            description=description
        )
        session.add(new_year)
        session.commit()
        st.success(f"Academic year {year} created successfully!")


def create_term(academic_year_id: int, name: str, start_date: date, end_date: date):
    """Create new term"""
    with get_session() as session:
        new_term = Term(
            academic_year_id=academic_year_id,
            name=name,
            start_date=datetime.combine(start_date, datetime.min.time()),
            end_date=datetime.combine(end_date, datetime.max.time())
        )
        session.add(new_term)
        session.commit()
        st.success(f"Term {name} created successfully!")


def create_calendar_event(title: str, description: str, event_type: str, start_date: date, start_time, end_date: date, end_time, is_all_day: bool, selected_class: str, selected_year: str):
    """Create calendar event"""
    user = get_current_user()
    
    with get_session() as session:
        # Combine date and time
        if is_all_day:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date or start_date, datetime.max.time())
        else:
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date or start_date, end_time) if end_date or end_time else None
        
        # Get class and academic year IDs
        class_id = None
        if selected_class != "All Classes":
            classes = session.exec(select(Class)).all()
            for cls in classes:
                if f"{cls.name} ({cls.category})" == selected_class:
                    class_id = cls.id
                    break
        
        academic_year_id = None
        if selected_year != "All Years":
            academic_year = session.exec(select(AcademicYear).where(AcademicYear.year == selected_year)).first()
            if academic_year:
                academic_year_id = academic_year.id
        
        new_event = CalendarEvent(
            title=title,
            description=description,
            event_type=event_type,
            start_date=start_datetime,
            end_date=end_datetime,
            is_all_day=is_all_day,
            class_id=class_id,
            academic_year_id=academic_year_id,
            created_by=user['id']
        )
        session.add(new_event)
        session.commit()
        st.success(f"Event '{title}' created successfully!")


def get_upcoming_events(days_ahead: int = 30) -> List[CalendarEvent]:
    """Get upcoming events"""
    today = datetime.now()
    future_date = today + timedelta(days=days_ahead)
    
    with get_session() as session:
        events = session.exec(
            select(CalendarEvent).where(
                CalendarEvent.start_date >= today,
                CalendarEvent.start_date <= future_date
            ).order_by(CalendarEvent.start_date)
        ).all()
    return events


# Additional helper functions for timetable and exam management would continue here...
# (Functions like create_timetable_entry, display_class_timetable, etc.)


def render_teacher_timetable():
    """Render timetable view for teachers"""
    st.header("⏰ My Timetable")
    st.info("Teacher timetable view - showing your assigned classes")
    
    # This would show the teacher's specific timetable
    # Implementation depends on how teacher-class assignments are handled


def render_exam_schedule_view():
    """Render exam schedule view for teachers"""
    st.header("📝 Exam Schedules")
    st.info("View upcoming exams for your classes")
    
    # This would show exams for classes the teacher is assigned to


def set_current_academic_year(year_id: int):
    """Set current academic year"""
    with get_session() as session:
        # Unset all current years
        current_years = session.exec(select(AcademicYear).where(AcademicYear.is_current == True)).all()
        for cy in current_years:
            cy.is_current = False
            session.add(cy)
        
        # Set new current year
        year = session.get(AcademicYear, year_id)
        if year:
            year.is_current = True
            session.add(year)
            session.commit()
            st.success(f"Academic year {year.year} set as current!")


def delete_academic_year(year_id: int):
    """Delete academic year"""
    with get_session() as session:
        year = session.get(AcademicYear, year_id)
        if year:
            session.delete(year)
            session.commit()
            st.success("Academic year deleted successfully!")


def set_current_term(term_id: int):
    """Set current term"""
    with get_session() as session:
        # Unset all current terms
        current_terms = session.exec(select(Term).where(Term.is_current == True)).all()
        for ct in current_terms:
            ct.is_current = False
            session.add(ct)
        
        # Set new current term
        term = session.get(Term, term_id)
        if term:
            term.is_current = True
            session.add(term)
            session.commit()
            st.success(f"Term {term.name} set as current!")


def delete_term(term_id: int):
    """Delete term"""
    with get_session() as session:
        term = session.get(Term, term_id)
        if term:
            session.delete(term)
            session.commit()
            st.success("Term deleted successfully!")


def get_timetable_for_day(selected_date: date):
    """Get timetable entries for a specific day"""
    day_of_week = selected_date.weekday()  # 0=Monday, 6=Sunday
    
    with get_session() as session:
        current_year, _ = get_current_academic_info()
        if not current_year:
            return []
        
        # This is a simplified version - in real implementation, you'd join with class/subject names
        timetables = session.exec(
            select(Timetable).where(
                Timetable.day_of_week == day_of_week,
                Timetable.academic_year_id == current_year.id
            ).order_by(Timetable.start_time)
        ).all()
    
    return timetables


def create_timetable_entry(class_id: int, subject_id: int, teacher_id: Optional[int], 
                          day_of_week: int, start_time, end_time, room: Optional[str], 
                          academic_year_id: int):
    """Create timetable entry"""
    with get_session() as session:
        new_entry = Timetable(
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            day_of_week=day_of_week,
            start_time=start_time.strftime("%H:%M"),
            end_time=end_time.strftime("%H:%M"),
            room=room,
            academic_year_id=academic_year_id
        )
        session.add(new_entry)
        session.commit()
        st.success("Timetable entry added successfully!")


def display_class_timetable(class_id: int, academic_year_id: int):
    """Display timetable for a class"""
    with get_session() as session:
        timetables = session.exec(
            select(Timetable).where(
                Timetable.class_id == class_id,
                Timetable.academic_year_id == academic_year_id
            ).order_by(Timetable.day_of_week, Timetable.start_time)
        ).all()
        
        if not timetables:
            st.info("No timetable entries for this class yet.")
            return
        
        # Group by day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day_num in range(7):
            day_entries = [t for t in timetables if t.day_of_week == day_num]
            if day_entries:
                st.subheader(days[day_num])
                
                for entry in day_entries:
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                    
                    # Get subject and teacher names
                    subject = session.get(Subject, entry.subject_id)
                    teacher = session.get(Teacher, entry.teacher_id) if entry.teacher_id else None
                    
                    with col1:
                        st.write(f"**{entry.start_time} - {entry.end_time}**")
                    with col2:
                        st.write(subject.name if subject else "Unknown Subject")
                    with col3:
                        st.write(f"{teacher.first_name} {teacher.last_name}" if teacher else "No Teacher")
                    with col4:
                        st.write(entry.room or "TBA")
                    with col5:
                        if st.button("Delete", key=f"delete_timetable_{entry.id}", type="secondary"):
                            session.delete(entry)
                            session.commit()
                            st.rerun()


def create_exam_schedule(title: str, subject_id: int, class_id: int, exam_date: date,
                        start_time, end_time, room: Optional[str], duration: int,
                        instructions: Optional[str], term_id: int):
    """Create exam schedule"""
    user = get_current_user()
    
    with get_session() as session:
        new_exam = ExamSchedule(
            title=title,
            subject_id=subject_id,
            class_id=class_id,
            exam_date=datetime.combine(exam_date, datetime.min.time()),
            start_time=start_time.strftime("%H:%M"),
            end_time=end_time.strftime("%H:%M"),
            room=room,
            duration_minutes=duration,
            instructions=instructions,
            term_id=term_id,
            created_by=user['id']
        )
        session.add(new_exam)
        session.commit()
        st.success(f"Exam '{title}' scheduled successfully!")


def get_upcoming_exams(term_id: int) -> List[ExamSchedule]:
    """Get upcoming exams for a term"""
    today = datetime.now()
    
    with get_session() as session:
        exams = session.exec(
            select(ExamSchedule).where(
                ExamSchedule.term_id == term_id,
                ExamSchedule.exam_date >= today
            ).order_by(ExamSchedule.exam_date)
        ).all()
    return exams


def delete_calendar_event(event_id: int):
    """Delete calendar event"""
    with get_session() as session:
        event = session.get(CalendarEvent, event_id)
        if event:
            session.delete(event)
            session.commit()
            st.success("Event deleted successfully!")


def delete_exam_schedule(exam_id: int):
    """Delete exam schedule"""
    with get_session() as session:
        exam = session.get(ExamSchedule, exam_id)
        if exam:
            session.delete(exam)
            session.commit()
            st.success("Exam schedule deleted successfully!")