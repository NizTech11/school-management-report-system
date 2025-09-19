"""
Enhanced Analytics Page - Advanced insights and predictive analytics
"""

import streamlit as st
import sys
from pathlib import Path

# Add the src directory to Python path for imports
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from components.enhanced_analytics import render_enhanced_analytics
from utils.rbac import get_current_user, has_permission


def main():
    """Main function for Enhanced Analytics page"""
    
    # Get current user
    user = get_current_user()
    if not user:
        st.error("Please log in to access this page")
        return
    
    # Check permissions for analytics access
    if not has_permission(user['role'], 'analytics.advanced'):
        st.error("You don't have permission to view enhanced analytics")
        st.info("Contact your administrator for access")
        return
    
    # Render the enhanced analytics dashboard
    render_enhanced_analytics()
    
    # Add help section
    with st.sidebar:
        st.markdown("---")
        st.subheader("📖 Enhanced Analytics Help")
        
        with st.expander("🔮 Predictive Analytics"):
            st.markdown("""
            **Features:**
            - Performance trend prediction
            - Student trajectory analysis
            - Confidence levels for predictions
            - Visual trend indicators
            
            **How to Use:**
            - Review trend directions for each student
            - Focus on high-confidence predictions
            - Use predictions for early intervention
            """)
        
        with st.expander("📈 Progress Tracking"):
            st.markdown("""
            **Features:**
            - Individual student progress timelines
            - Rolling average trends
            - Subject-wise improvement tracking
            - Class progress comparisons
            
            **How to Use:**
            - Select students to view detailed progress
            - Monitor improvement rates
            - Identify consistent performers
            """)
        
        with st.expander("⚠️ Risk Identification"):
            st.markdown("""
            **Risk Factors:**
            - Low performance scores
            - Declining trends
            - Inconsistent results
            - Insufficient assessments
            
            **Risk Levels:**
            - 🔴 High Risk: Immediate intervention needed
            - 🟡 Warning: Monitor closely
            - 🟢 Safe: Performing well
            """)
        
        with st.expander("🔍 Comparative Analysis"):
            st.markdown("""
            **Features:**
            - Class performance comparison
            - Subject difficulty analysis
            - Performance consistency metrics
            - Ranking and benchmarking
            
            **Use Cases:**
            - Identify top-performing classes
            - Compare subject difficulties
            - Benchmark against standards
            """)
        
        with st.expander("🎯 Performance Insights"):
            st.markdown("""
            **Features:**
            - Automated insight generation
            - Correlation analysis
            - Performance distribution
            - Key metric relationships
            
            **Benefits:**
            - Quick understanding of trends
            - Data-driven recommendations
            - Statistical insights
            """)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Enhanced Analytics",
        page_icon="📊",
        layout="wide"
    )
    main()