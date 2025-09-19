"""
Enhanced Analytics Dashboard with Advanced Features
Includes predictive            student = students.get(mark.student_id)
            subject = subjects.get(mark.subject_id)
            if student and subject:
                class_obj = classes.get(student.class_id)
                
                if class_obj:  # Only add if all data is available
                    data.append({
                        'id': mark.id,
                        'student_id': mark.student_id,
                        'subject_id': mark.subject_id,
                        'score': mark.score,
                        'term': mark.term,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'class_id': student.class_id,
                        'subject_name': subject.name,
                        'subject_code': subject.code,
                        'subject_category': subject.category,
                        'class_name': class_obj.names tracking, comparative analysis, and risk identification
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from services.db import get_session, Student, Subject, Mark, Class
from sqlmodel import select, and_, func
from components.dashboard import get_analytics_data

# Optional imports for advanced analytics
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    LinearRegression = None
    StandardScaler = None


def render_enhanced_analytics():
    """Main enhanced analytics dashboard"""
    st.title("📊 Enhanced Analytics Dashboard")
    st.markdown("*Advanced insights with predictive analytics and risk identification*")
    
    # Show sklearn availability status
    if not SKLEARN_AVAILABLE:
        st.warning("⚠️ **Limited Functionality**: Advanced predictive features are disabled. To enable them, install scikit-learn: `pip install scikit-learn`")
        st.info("💡 Basic analytics are still available without advanced machine learning features.")
    else:
        st.success("✅ **Full Functionality**: All advanced analytics features are available.")
    
    # Get enhanced data
    students, subjects, marks_data = get_analytics_data()
    enhanced_data = prepare_enhanced_analytics_data()
    
    if not marks_data:
        st.warning("No performance data available. Please add some marks first.")
        return
    
    # Analytics navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔮 Predictive Analytics",
        "📈 Progress Tracking", 
        "⚠️ Risk Identification",
        "🔍 Comparative Analysis",
        "🎯 Performance Insights"
    ])
    
    with tab1:
        render_predictive_analytics(enhanced_data)
    
    with tab2:
        render_progress_tracking(enhanced_data)
    
    with tab3:
        render_risk_identification(enhanced_data)
    
    with tab4:
        render_comparative_analysis(enhanced_data)
    
    with tab5:
        render_performance_insights(enhanced_data)


def prepare_enhanced_analytics_data():
    """Prepare enhanced analytics data with temporal and predictive features"""
    with get_session() as session:
        # Get all marks first
        marks = session.exec(select(Mark)).all()
        if not marks:
            return pd.DataFrame()
        
        # Get related data
        students = {s.id: s for s in session.exec(select(Student)).all()}
        subjects = {s.id: s for s in session.exec(select(Subject)).all()}
        classes = {c.id: c for c in session.exec(select(Class)).all()}
        
        # Convert to DataFrame manually
        data = []
        for mark in marks:
            student = students.get(mark.student_id)
            subject = subjects.get(mark.subject_id)
            if student and subject:
                class_obj = classes.get(student.class_id)
                
                if class_obj:  # Only add if all data is available
                    data.append({
                        'id': mark.id,
                        'student_id': mark.student_id,
                        'subject_id': mark.subject_id,
                        'score': mark.score,
                        'term': mark.term,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'class_id': student.class_id,
                        'aggregate': student.aggregate,
                        'subject_name': subject.name,
                        'subject_code': subject.code,
                        'class_name': class_obj.name
                    })
        
        marks_df = pd.DataFrame(data)
        
        if marks_df.empty:
            return pd.DataFrame()
        
        # Add derived features
        marks_df['student_name'] = marks_df['first_name'] + ' ' + marks_df['last_name']
        
        # Since we don't have timestamps, create synthetic time progression
        marks_df['record_index'] = marks_df.groupby('student_id').cumcount()
        
        # Calculate student-level aggregations
        student_stats = marks_df.groupby('student_id').agg({
            'score': ['mean', 'std', 'count', 'min', 'max'],
            'term': 'nunique',
            'subject_id': 'nunique'
        }).round(2)
        
        student_stats.columns = [f"{col[0]}_{col[1]}" for col in student_stats.columns]
        student_stats.reset_index(inplace=True)
        
        # Merge student statistics back to main dataframe
        marks_df = marks_df.merge(student_stats, on='student_id', how='left')
        
        # Add trends and predictions based on record order
        marks_df = add_trend_analysis_simple(marks_df)
        marks_df = add_performance_predictions_simple(marks_df)
        
        return marks_df


def add_trend_analysis_simple(df: pd.DataFrame) -> pd.DataFrame:
    """Add trend analysis for each student based on record order"""
    df_with_trends = df.copy()
    
    # Calculate rolling averages and trends
    df_with_trends = df_with_trends.sort_values(['student_id', 'record_index'])
    
    # Group by student and calculate trends
    trend_data = []
    
    for student_id in df_with_trends['student_id'].unique():
        student_data = df_with_trends[df_with_trends['student_id'] == student_id].copy()
        
        if len(student_data) >= 3:  # Need at least 3 points for trend
            # Calculate rolling average (window of 3)
            student_data['rolling_avg'] = student_data['score'].rolling(window=3, min_periods=1).mean()
            
            # Calculate trend (slope of linear regression)
            x = student_data['record_index'].values.reshape(-1, 1)
            y = student_data['score'].values
            
            try:
                if SKLEARN_AVAILABLE and LinearRegression is not None:
                    model = LinearRegression()
                    model.fit(x, y)
                    trend_slope = model.coef_[0]
                else:
                    # Simple trend calculation without sklearn
                    if len(x) >= 2:
                        trend_slope = (y[-1] - y[0]) / (len(y) - 1)
                    else:
                        trend_slope = 0
                
                student_data['trend_slope'] = trend_slope
                student_data['trend_direction'] = np.where(
                    trend_slope > 0.5, 'Improving',
                    np.where(trend_slope < -0.5, 'Declining', 'Stable')
                )
            except:
                student_data['trend_slope'] = 0
                student_data['trend_direction'] = 'Stable'
        else:
            student_data['rolling_avg'] = student_data['score']
            student_data['trend_slope'] = 0
            student_data['trend_direction'] = 'Insufficient Data'
        
        trend_data.append(student_data)
    
    if trend_data:
        df_with_trends = pd.concat(trend_data, ignore_index=True)
    
    return df_with_trends


def add_performance_predictions_simple(df: pd.DataFrame) -> pd.DataFrame:
    """Add performance predictions for students based on record order"""
    df_with_predictions = df.copy()
    
    prediction_data = []
    
    for student_id in df_with_predictions['student_id'].unique():
        student_data = df_with_predictions[df_with_predictions['student_id'] == student_id].copy()
        
        if len(student_data) >= 4:  # Need sufficient data for prediction
            try:
                # Prepare features for prediction
                student_data = student_data.sort_values('record_index')
                x = student_data['record_index'].values.reshape(-1, 1)
                y = student_data['score'].values
                
                # Simple linear regression for trend prediction
                if SKLEARN_AVAILABLE and LinearRegression is not None:
                    model = LinearRegression()
                    model.fit(x, y)
                    
                    # Predict next score
                    next_x = np.array([[student_data['record_index'].max() + 1]])
                    predicted_score = model.predict(next_x)[0]
                else:
                    # Simple prediction without sklearn
                    if len(y) >= 2:
                        recent_trend = (y[-1] - y[-2]) if len(y) >= 2 else 0
                        predicted_score = y[-1] + recent_trend
                    else:
                        predicted_score = y[-1] if len(y) > 0 else 50
                
                # Bound prediction between 0 and 100
                predicted_score = max(0, min(100, predicted_score))
                
                student_data['predicted_next_score'] = predicted_score
                student_data['prediction_confidence'] = calculate_prediction_confidence(y, model.predict(x))
                
            except:
                student_data['predicted_next_score'] = student_data['score'].mean()
                student_data['prediction_confidence'] = 'Low'
        else:
            student_data['predicted_next_score'] = student_data['score'].mean()
            student_data['prediction_confidence'] = 'Insufficient Data'
        
        prediction_data.append(student_data)
    
    if prediction_data:
        df_with_predictions = pd.concat(prediction_data, ignore_index=True)
    
    return df_with_predictions


def calculate_prediction_confidence(actual: np.ndarray, predicted: np.ndarray) -> str:
    """Calculate confidence level of predictions"""
    if len(actual) < 3:
        return 'Low'
    
    mse = np.mean((actual - predicted) ** 2)
    
    if mse < 25:  # Very low error
        return 'High'
    elif mse < 100:  # Moderate error
        return 'Medium'
    else:
        return 'Low'


def render_predictive_analytics(df: pd.DataFrame):
    """Render predictive analytics dashboard"""
    st.header("🔮 Predictive Analytics")
    
    if df.empty:
        st.info("No data available for predictive analytics")
        return
    
    # Get latest predictions for each student
    latest_predictions = df.groupby('student_id').last().reset_index()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        improving_students = len(latest_predictions[latest_predictions['trend_direction'] == 'Improving'])
        st.metric("Improving Trends", improving_students)
    
    with col2:
        declining_students = len(latest_predictions[latest_predictions['trend_direction'] == 'Declining'])
        st.metric("Declining Trends", declining_students, delta=f"-{declining_students}")
    
    with col3:
        high_confidence = len(latest_predictions[latest_predictions['prediction_confidence'] == 'High'])
        st.metric("High Confidence Predictions", high_confidence)
    
    with col4:
        avg_predicted = latest_predictions['predicted_next_score'].mean()
        st.metric("Avg Predicted Score", f"{avg_predicted:.1f}%")
    
    st.divider()
    
    # Predictive charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance prediction scatter plot
        fig = px.scatter(
            latest_predictions,
            x='score',
            y='predicted_next_score',
            color='trend_direction',
            hover_data=['student_name', 'prediction_confidence'],
            title="Current vs Predicted Performance",
            labels={'score': 'Current Average Score', 'predicted_next_score': 'Predicted Next Score'}
        )
        
        # Add diagonal line for reference
        fig.add_shape(
            type="line",
            x0=0, y0=0, x1=100, y1=100,
            line=dict(dash="dash", color="gray")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Trend distribution
        trend_counts = latest_predictions['trend_direction'].value_counts()
        fig = px.pie(
            values=trend_counts.values,
            names=trend_counts.index,
            title="Student Performance Trends",
            color_discrete_map={
                'Improving': 'green',
                'Declining': 'red',
                'Stable': 'blue',
                'Insufficient Data': 'gray'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Detailed predictions table
    st.subheader("📋 Detailed Predictions")
    
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        selected_trend = st.selectbox(
            "Filter by Trend",
            options=['All'] + list(latest_predictions['trend_direction'].unique())
        )
    
    with col2:
        selected_confidence = st.selectbox(
            "Filter by Confidence",
            options=['All'] + list(latest_predictions['prediction_confidence'].unique())
        )
    
    # Apply filters
    filtered_predictions = latest_predictions.copy()
    if selected_trend != 'All':
        filtered_predictions = filtered_predictions[filtered_predictions['trend_direction'] == selected_trend]
    if selected_confidence != 'All':
        filtered_predictions = filtered_predictions[filtered_predictions['prediction_confidence'] == selected_confidence]
    
    # Display predictions table
    display_cols = ['student_name', 'class_name', 'score', 'predicted_next_score', 
                   'trend_direction', 'prediction_confidence']
    
    if not filtered_predictions.empty:
        predictions_table = filtered_predictions[display_cols].copy()
        predictions_table['score'] = predictions_table['score'].round(1)
        predictions_table['predicted_next_score'] = predictions_table['predicted_next_score'].round(1)
        predictions_table = predictions_table.rename(columns={
            'student_name': 'Student',
            'class_name': 'Class',
            'score': 'Current Avg',
            'predicted_next_score': 'Predicted Score',
            'trend_direction': 'Trend',
            'prediction_confidence': 'Confidence'
        })
        
        st.dataframe(predictions_table, use_container_width=True)
    else:
        st.info("No predictions match the selected filters.")


def render_progress_tracking(df: pd.DataFrame):
    """Render progress tracking dashboard"""
    st.header("📈 Progress Tracking")
    
    if df.empty:
        st.info("No data available for progress tracking")
        return
    
    # Student selection for detailed tracking
    students = df['student_name'].unique()
    selected_student = st.selectbox("Select Student for Detailed Progress", students)
    
    if selected_student:
        student_data = df[df['student_name'] == selected_student].sort_values('record_index')
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Progress timeline based on record order
            fig = go.Figure()
            
            # Add actual scores
            fig.add_trace(go.Scatter(
                x=student_data['record_index'],
                y=student_data['score'],
                mode='markers+lines',
                name='Actual Scores',
                line=dict(color='blue', width=2),
                marker=dict(size=8)
            ))
            
            # Add rolling average if available
            if 'rolling_avg' in student_data.columns:
                fig.add_trace(go.Scatter(
                    x=student_data['record_index'],
                    y=student_data['rolling_avg'],
                    mode='lines',
                    name='Trend Line',
                    line=dict(color='red', width=2, dash='dash')
                ))
            
            fig.update_layout(
                title=f"Progress Timeline - {selected_student}",
                xaxis_title="Assessment Number",
                yaxis_title="Score (%)",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Progress metrics
            if len(student_data) > 1:
                latest_score = student_data['score'].iloc[-1]
                first_score = student_data['score'].iloc[0]
                improvement = latest_score - first_score
                
                st.metric("Latest Score", f"{latest_score:.1f}%")
                st.metric("Total Improvement", f"{improvement:.1f}%", delta=f"{improvement:.1f}%")
                st.metric("Best Score", f"{student_data['score'].max():.1f}%")
                st.metric("Assessments Taken", len(student_data))
        
        # Subject-wise progress
        st.subheader(f"Subject-wise Progress - {selected_student}")
        
        subject_progress = student_data.groupby('subject_name').agg({
            'score': ['mean', 'count', 'first', 'last']
        }).round(1)
        
        subject_progress.columns = ['Average', 'Count', 'First', 'Latest']
        subject_progress['Improvement'] = (subject_progress['Latest'] - subject_progress['First']).round(1)
        
        st.dataframe(subject_progress, use_container_width=True)
    
    st.divider()
    
    # Class progress comparison by term
    st.subheader("🏫 Class Progress by Term")
    
    class_term_progress = df.groupby(['class_name', 'term']).agg({
        'score': 'mean'
    }).reset_index()
    
    if not class_term_progress.empty:
        fig = px.line(
            class_term_progress,
            x='term',
            y='score',
            color='class_name',
            title="Average Class Performance by Term",
            labels={'score': 'Average Score (%)', 'term': 'Term'}
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_risk_identification(df: pd.DataFrame):
    """Render risk identification dashboard"""
    st.header("⚠️ Risk Identification")
    
    if df.empty:
        st.info("No data available for risk analysis")
        return
    
    # Calculate risk factors
    latest_data = df.groupby('student_id').last().reset_index()
    
    # Define risk criteria
    at_risk_students = []
    warning_students = []
    
    for _, student in latest_data.iterrows():
        risk_score = 0
        risk_factors = []
        
        # Low performance risk
        if student['score'] < 50:
            risk_score += 3
            risk_factors.append("Low performance (<50%)")
        elif student['score'] < 65:
            risk_score += 1
            risk_factors.append("Below average performance")
        
        # Declining trend risk
        if student.get('trend_direction') == 'Declining':
            risk_score += 2
            risk_factors.append("Declining trend")
        
        # Low assessment count risk (check if column exists)
        score_count = student.get('score_count', 0)
        if score_count and score_count < 3:
            risk_score += 1
            risk_factors.append("Insufficient assessments")
        
        # Consistency risk (high standard deviation)
        score_std = student.get('score_std', 0)
        if score_std and score_std > 20:
            risk_score += 1
            risk_factors.append("Inconsistent performance")
        
        student_info = {
            'student_name': student['student_name'],
            'class_name': student['class_name'],
            'current_score': student['score'],
            'trend': student.get('trend_direction', 'Unknown'),
            'risk_score': risk_score,
            'risk_factors': risk_factors
        }
        
        if risk_score >= 4:
            at_risk_students.append(student_info)
        elif risk_score >= 2:
            warning_students.append(student_info)
    
    # Display risk summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔴 High Risk Students", len(at_risk_students))
    
    with col2:
        st.metric("🟡 Warning Students", len(warning_students))
    
    with col3:
        total_students = len(latest_data)
        safe_students = total_students - len(at_risk_students) - len(warning_students)
        st.metric("🟢 Safe Students", safe_students)
    
    st.divider()
    
    # Risk visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk distribution
        risk_distribution = {
            'High Risk': len(at_risk_students),
            'Warning': len(warning_students),
            'Safe': safe_students
        }
        
        fig = px.pie(
            values=list(risk_distribution.values()),
            names=list(risk_distribution.keys()),
            title="Student Risk Distribution",
            color_discrete_map={
                'High Risk': 'red',
                'Warning': 'orange', 
                'Safe': 'green'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk factors frequency
        all_factors = []
        for student in at_risk_students + warning_students:
            all_factors.extend(student['risk_factors'])
        
        if all_factors:
            factor_counts = pd.Series(all_factors).value_counts()
            
            fig = px.bar(
                x=factor_counts.index,
                y=factor_counts.values,
                title="Most Common Risk Factors",
                labels={'x': 'Risk Factor', 'y': 'Number of Students'}
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed risk tables
    st.divider()
    
    if at_risk_students:
        st.subheader("🔴 High Risk Students")
        st.error("These students require immediate attention and intervention")
        
        risk_df = pd.DataFrame(at_risk_students)
        risk_df['risk_factors_str'] = risk_df['risk_factors'].apply(lambda x: ', '.join(x))
        
        display_risk = risk_df[['student_name', 'class_name', 'current_score', 'trend', 'risk_factors_str']].copy()
        display_risk = display_risk.rename(columns={
            'student_name': 'Student',
            'class_name': 'Class',
            'current_score': 'Current Score',
            'trend': 'Trend',
            'risk_factors_str': 'Risk Factors'
        })
        
        st.dataframe(display_risk, use_container_width=True)
    
    if warning_students:
        st.subheader("🟡 Warning Students")
        st.warning("These students need monitoring and support")
        
        warning_df = pd.DataFrame(warning_students)
        warning_df['risk_factors_str'] = warning_df['risk_factors'].apply(lambda x: ', '.join(x))
        
        display_warning = warning_df[['student_name', 'class_name', 'current_score', 'trend', 'risk_factors_str']].copy()
        display_warning = display_warning.rename(columns={
            'student_name': 'Student',
            'class_name': 'Class',
            'current_score': 'Current Score',
            'trend': 'Trend',
            'risk_factors_str': 'Risk Factors'
        })
        
        st.dataframe(display_warning, use_container_width=True)


def render_comparative_analysis(df: pd.DataFrame):
    """Render comparative analysis dashboard"""
    st.header("🔍 Comparative Analysis")
    
    if df.empty:
        st.info("No data available for comparative analysis")
        return
    
    # Class comparison
    st.subheader("🏫 Class Performance Comparison")
    
    class_stats = df.groupby('class_name').agg({
        'score': ['mean', 'std', 'count'],
        'student_id': 'nunique'
    }).round(2)
    
    class_stats.columns = ['Avg_Score', 'Std_Dev', 'Total_Assessments', 'Total_Students']
    class_stats = class_stats.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Class performance radar chart
        fig = go.Figure()
        
        for class_name in class_stats['class_name']:
            class_data = class_stats[class_stats['class_name'] == class_name].iloc[0]
            
            fig.add_trace(go.Scatterpolar(
                r=[
                    class_data['Avg_Score'],
                    100 - class_data['Std_Dev'],  # Invert std_dev (lower is better)
                    min(class_data['Total_Assessments'] * 10, 100),  # Scale assessments
                    min(class_data['Total_Students'] * 5, 100)  # Scale students
                ],
                theta=['Avg Performance', 'Consistency', 'Assessment Activity', 'Class Size'],
                fill='toself',
                name=class_name
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Class Performance Comparison"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Class ranking
        class_ranking = class_stats.sort_values('Avg_Score', ascending=False).copy()
        class_ranking['Rank'] = range(1, len(class_ranking) + 1)
        
        fig = px.bar(
            class_ranking,
            x='class_name',
            y='Avg_Score',
            title="Class Performance Ranking",
            text='Rank',
            labels={'class_name': 'Class', 'Avg_Score': 'Average Score (%)'}
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Subject comparison
    st.subheader("📚 Subject Performance Comparison")
    
    subject_stats = df.groupby('subject_name').agg({
        'score': ['mean', 'std', 'count'],
        'student_id': 'nunique'
    }).round(2)
    
    subject_stats.columns = ['Avg_Score', 'Std_Dev', 'Total_Assessments', 'Total_Students']
    subject_stats = subject_stats.reset_index().sort_values('Avg_Score', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            subject_stats,
            x='subject_name',
            y='Avg_Score',
            title="Subject Performance Ranking",
            labels={'subject_name': 'Subject', 'Avg_Score': 'Average Score (%)'}
        )
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            subject_stats,
            x='Avg_Score',
            y='Std_Dev',
            size='Total_Students',
            hover_data=['subject_name', 'Total_Assessments'],
            title="Subject Performance vs Consistency",
            labels={'Avg_Score': 'Average Score (%)', 'Std_Dev': 'Standard Deviation'}
        )
        st.plotly_chart(fig, use_container_width=True)


def render_performance_insights(df: pd.DataFrame):
    """Render performance insights dashboard"""
    st.header("🎯 Performance Insights")
    
    if df.empty:
        st.info("No data available for performance insights")
        return
    
    # Key insights
    st.subheader("💡 Key Insights")
    
    insights = generate_performance_insights(df)
    
    for insight in insights:
        if insight['type'] == 'success':
            st.success(f"✅ {insight['message']}")
        elif insight['type'] == 'warning':
            st.warning(f"⚠️ {insight['message']}")
        elif insight['type'] == 'info':
            st.info(f"ℹ️ {insight['message']}")
    
    st.divider()
    
    # Performance distribution analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution
        fig = px.histogram(
            df,
            x='score',
            nbins=20,
            title="Overall Score Distribution",
            labels={'score': 'Score (%)', 'count': 'Number of Assessments'}
        )
        fig.add_vline(x=df['score'].mean(), line_dash="dash", line_color="red", 
                     annotation_text=f"Mean: {df['score'].mean():.1f}%")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance by time of day (if we had that data)
        # For now, let's show performance by term
        if 'term' in df.columns:
            term_performance = df.groupby('term')['score'].mean().sort_values(ascending=False)
            
            fig = px.bar(
                x=term_performance.index,
                y=term_performance.values,
                title="Performance by Term",
                labels={'x': 'Term', 'y': 'Average Score (%)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.subheader("📊 Performance Correlations")
    
    # Calculate correlations between different metrics
    student_metrics = df.groupby('student_id').agg({
        'score': ['mean', 'std', 'count'],
        'subject_id': 'nunique'
    }).round(2)
    
    student_metrics.columns = ['avg_score', 'score_std', 'assessment_count', 'subject_count']
    
    if len(student_metrics) > 1:
        correlation_matrix = student_metrics.corr()
        
        fig = px.imshow(
            correlation_matrix,
            title="Student Metrics Correlation Matrix",
            labels=dict(color="Correlation"),
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        st.write("**Correlation Insights:**")
        strong_correlations = []
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                try:
                    corr_value = correlation_matrix.iloc[i, j]
                    if pd.notna(corr_value) and isinstance(corr_value, (int, float)) and abs(corr_value) > 0.5:
                        col1_name = correlation_matrix.columns[i]
                        col2_name = correlation_matrix.columns[j]
                        strong_correlations.append(f"**{col1_name}** and **{col2_name}**: {corr_value:.2f}")
                except (TypeError, ValueError):
                    continue  # Skip invalid correlation values
        
        if strong_correlations:
            for corr in strong_correlations:
                st.write(f"• {corr}")
        else:
            st.write("• No strong correlations found between metrics")


def generate_performance_insights(df: pd.DataFrame) -> List[Dict]:
    """Generate automated insights from the data"""
    insights = []
    
    # Overall performance insight
    avg_score = df['score'].mean()
    if avg_score >= 80:
        insights.append({
            'type': 'success',
            'message': f"Overall performance is excellent with an average score of {avg_score:.1f}%"
        })
    elif avg_score >= 70:
        insights.append({
            'type': 'info', 
            'message': f"Overall performance is good with an average score of {avg_score:.1f}%"
        })
    else:
        insights.append({
            'type': 'warning',
            'message': f"Overall performance needs improvement with an average score of {avg_score:.1f}%"
        })
    
    # Trend insights
    if 'trend_direction' in df.columns:
        latest_trends = df.groupby('student_id')['trend_direction'].last()
        improving_pct = (latest_trends == 'Improving').mean() * 100
        declining_pct = (latest_trends == 'Declining').mean() * 100
        
        if improving_pct > declining_pct:
            insights.append({
                'type': 'success',
                'message': f"{improving_pct:.1f}% of students show improving trends vs {declining_pct:.1f}% declining"
            })
        else:
            insights.append({
                'type': 'warning',
                'message': f"{declining_pct:.1f}% of students show declining trends - intervention may be needed"
            })
    
    # Class performance insights
    class_performance = df.groupby('class_name')['score'].mean()
    best_class = class_performance.idxmax()
    worst_class = class_performance.idxmin()
    
    if class_performance.max() - class_performance.min() > 15:
        insights.append({
            'type': 'warning',
            'message': f"Significant performance gap between classes: {best_class} ({class_performance.max():.1f}%) vs {worst_class} ({class_performance.min():.1f}%)"
        })
    
    # Subject performance insights
    subject_performance = df.groupby('subject_name')['score'].mean()
    best_subject = subject_performance.idxmax()
    worst_subject = subject_performance.idxmin()
    
    insights.append({
        'type': 'info',
        'message': f"Strongest subject: {best_subject} ({subject_performance.max():.1f}%), Weakest: {worst_subject} ({subject_performance.min():.1f}%)"
    })
    
    return insights