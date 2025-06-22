"""
EdTech Ranking 2025 - Main Streamlit Application
A comprehensive ranking system for Vietnamese EdTech platforms
"""

import streamlit as st
import os
import sys

# Configure page settings
st.set_page_config(
    page_title="EdTech Ranking 2025",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import modules with error handling
try:
    from webpages.app import main_app
    from webpages.web import main_web
    from webpages.ranking import main_ranking
    from webpages.feedback import main_feedback
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required files are present in the webpages directory.")
    st.stop()

def main():
    """Main application function with navigation"""
    
    # Sidebar navigation
    st.sidebar.title("🎓 EdTech Ranking 2025")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "📱 App Analysis", "🌐 Website Analysis", "📊 Rankings", "💬 Feedback"],
        index=0
    )
    
    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "📱 App Analysis":
        try:
            main_app()
        except Exception as e:
            st.error(f"Error loading App Analysis: {e}")
            st.info("Please check your database connection and try again.")
    elif page == "🌐 Website Analysis":
        try:
            main_web()
        except Exception as e:
            st.error(f"Error loading Website Analysis: {e}")
            st.info("Please check your database connection and try again.")
    elif page == "📊 Rankings":
        try:
            main_ranking()
        except Exception as e:
            st.error(f"Error loading Rankings: {e}")
            st.info("Please check your database connection and try again.")
    elif page == "💬 Feedback":
        try:
            main_feedback()
        except Exception as e:
            st.error(f"Error loading Feedback: {e}")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**EdTech Ranking 2025**")
    st.sidebar.markdown("Comprehensive analysis of Vietnamese EdTech platforms")

def show_home_page():
    """Display the home page"""
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #4CAF50; font-size: 3rem; margin-bottom: 0.5rem;'>
                🎓 EdTech Ranking 2025
            </h1>
            <h3 style='color: #666; font-weight: 300;'>
                Comprehensive Analysis of Vietnamese EdTech Platforms
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            ### 🚀 Welcome to EdTech Ranking 2025
            
            This platform provides comprehensive analysis and ranking of Vietnamese EdTech platforms, 
            covering both mobile applications and websites across multiple evaluation criteria.
            
            #### 📊 What We Analyze:
            - **📱 Mobile Applications**: 590+ apps from Google Play and App Store
            - **🌐 Websites**: Comprehensive website evaluation
            - **🔍 Multi-Criteria Assessment**: Speed, Security, Accessibility, Authority, Readability
            - **📈 Market Analysis**: Trends, rankings, and insights
            
            #### 👥 For Stakeholders:
            - **👨‍🏫 Teachers**: Find the best educational tools
            - **👨‍👩‍👧‍👦 Parents**: Choose safe and effective learning platforms
            - **💼 Investors**: Market analysis and opportunities
            - **🏢 Administrators**: Benchmark and compare platforms
            - **📊 Analysts**: Data-driven insights and trends
        """)
        
        # Quick stats
        st.markdown("---")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("📱 Apps Analyzed", "590+")
        
        with col_stat2:
            st.metric("🌐 Websites", "200+")
        
        with col_stat3:
            st.metric("📊 Criteria", "5")
        
        with col_stat4:
            st.metric("🎯 Accuracy", "95%+")
    
    # Features section
    st.markdown("---")
    st.markdown("### 🔧 Platform Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
            #### 📱 App Analysis
            - Download trends and user engagement
            - Sentiment analysis of user reviews
            - Performance metrics and ratings
            - Comparative analysis tools
            
            #### 🌐 Website Analysis
            - Speed and performance evaluation
            - Security assessment
            - Accessibility compliance
            - SEO and authority metrics
        """)
    
    with feature_col2:
        st.markdown("""
            #### 📊 Rankings & Insights
            - Real-time ranking updates
            - Market trend analysis
            - Detailed comparison tools
            - Export and reporting features
            
            #### 🔒 Security & Privacy
            - Secure database connections
            - Environment-based configuration
            - Data privacy compliance
            - Regular security updates
        """)
    
    # Getting started
    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    
    st.info("""
        **Ready to explore?** Use the navigation menu on the left to:
        
        1. **📱 App Analysis** - Analyze mobile application performance and user sentiment
        2. **🌐 Website Analysis** - Evaluate website quality and performance metrics  
        3. **📊 Rankings** - View comprehensive rankings and comparisons
        4. **💬 Feedback** - Share your thoughts and suggestions
    """)

if __name__ == "__main__":
    main()
