"""
Reddit Analytics Integration Platform - Streamlit Dashboard
Interactive UI for configuring, running, and visualizing Reddit data analytics
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import pathlib

# Add the project root to the path
project_root = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from streamlit_utils.config_manager import (
    get_reddit_extraction_config,
    update_reddit_extraction_config,
    validate_config,
    get_aws_config
)
from streamlit_utils.reddit_api import (
    validate_subreddit,
    get_subreddit_info,
    test_reddit_credentials
)
from streamlit_utils.data_loader import (
    load_data,
    get_data_summary,
    export_to_csv
)
from streamlit_utils.visualizations import (
    create_time_series_chart,
    create_top_posts_chart,
    create_author_chart,
    create_engagement_scatter,
    create_distribution_chart,
    create_pie_chart,
    generate_wordcloud,
    create_heatmap
)

# Page configuration
st.set_page_config(
    page_title="Reddit Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF4500, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("# 🎯 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["🏠 Home", "⚙️ Configuration", "📊 Data Viewer", "📈 Analytics Dashboard", "🔧 Pipeline Control"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Quick Info")

# Show current configuration in sidebar
try:
    current_config = get_reddit_extraction_config()
    st.sidebar.info(f"""
    **Current Subreddit:** r/{current_config['subreddit']}  
    **Time Filter:** {current_config['time_filter']}  
    **Post Limit:** {current_config['limit'] if current_config['limit'] else 'No limit'}
    """)
except Exception as e:
    st.sidebar.error("Error loading configuration")

# ============================================================================
# HOME PAGE
# ============================================================================
if page == "🏠 Home":
    st.markdown('<h1 class="main-header">📊 Reddit Analytics Platform</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the **Reddit Analytics Integration Platform**! This interactive dashboard allows you to:
    
    - 🎯 **Configure** which subreddit to analyze
    - 📊 **View** extracted Reddit data in an interactive table
    - 📈 **Visualize** trends, engagement metrics, and insights
    - ⚙️ **Control** the data pipeline settings
    """)
    
    # System status
    st.markdown("## 🔍 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check configuration
        is_valid, errors = validate_config()
        if is_valid:
            st.success("✅ Configuration Valid")
        else:
            st.error("❌ Configuration Issues")
            with st.expander("View Errors"):
                for error in errors:
                    st.write(f"- {error}")
    
    with col2:
        # Check Reddit API
        api_valid, api_error = test_reddit_credentials()
        if api_valid:
            st.success("✅ Reddit API Connected")
        else:
            st.error("❌ Reddit API Error")
            if api_error:
                with st.expander("View Error"):
                    st.write(api_error)
    
    with col3:
        # Check data availability
        with st.spinner("Checking data..."):
            df = load_data(prefer_redshift=False)
            if df is not None and not df.empty:
                st.success(f"✅ Data Available ({len(df)} posts)")
            else:
                st.warning("⚠️ No Data Found")
    
    # Quick stats
    if df is not None and not df.empty:
        st.markdown("## 📊 Quick Statistics")
        
        summary = get_data_summary(df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Posts", f"{summary['total_posts']:,}")
        
        with col2:
            st.metric("Total Score", f"{summary['total_score']:,}")
        
        with col3:
            st.metric("Total Comments", f"{summary['total_comments']:,}")
        
        with col4:
            st.metric("Unique Authors", f"{summary['unique_authors']:,}")
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 Getting Started
    
    1. **Configure Your Subreddit**: Go to the ⚙️ Configuration page to set which subreddit to analyze
    2. **Run the Pipeline**: Use the 🔧 Pipeline Control page to trigger data extraction
    3. **View Your Data**: Check the 📊 Data Viewer to browse extracted posts
    4. **Analyze Trends**: Explore the 📈 Analytics Dashboard for insights
    """)

# ============================================================================
# CONFIGURATION PAGE
# ============================================================================
elif page == "⚙️ Configuration":
    st.markdown('<h1 class="main-header">⚙️ Configuration Manager</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Configure the Reddit extraction settings. Changes will be saved to `configuration.conf` 
    and will be used by the Airflow pipeline on the next run.
    """)
    
    # Load current configuration
    current_config = get_reddit_extraction_config()
    
    st.markdown("## 🎯 Reddit Extraction Settings")
    
    with st.form("config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            subreddit = st.text_input(
                "Subreddit Name",
                value=current_config['subreddit'],
                help="Enter the subreddit name without 'r/' prefix"
            )
            
            time_filter = st.selectbox(
                "Time Filter",
                options=["hour", "day", "week", "month", "year", "all"],
                index=["hour", "day", "week", "month", "year", "all"].index(current_config['time_filter']),
                help="Time period for extracting top posts"
            )
        
        with col2:
            limit_option = st.radio(
                "Post Limit",
                options=["No Limit", "Custom Limit"],
                index=0 if current_config['limit'] is None else 1
            )
            
            if limit_option == "Custom Limit":
                limit = st.number_input(
                    "Number of Posts",
                    min_value=1,
                    max_value=1000,
                    value=current_config['limit'] if current_config['limit'] else 100,
                    help="Maximum number of posts to extract"
                )
            else:
                limit = None
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            validate_btn = st.form_submit_button("🔍 Validate Subreddit", use_container_width=True)
        
        with col2:
            save_btn = st.form_submit_button("💾 Save Configuration", use_container_width=True, type="primary")
    
    # Validate subreddit
    if validate_btn:
        with st.spinner(f"Validating r/{subreddit}..."):
            is_valid, error_msg = validate_subreddit(subreddit)
            
            if is_valid:
                st.success(f"✅ Subreddit r/{subreddit} is valid and accessible!")
                
                # Show subreddit info
                info = get_subreddit_info(subreddit)
                if info:
                    st.markdown("### 📋 Subreddit Information")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Subscribers", f"{info['subscribers']:,}")
                    
                    with col2:
                        st.metric("NSFW", "Yes" if info['over18'] else "No")
                    
                    with col3:
                        st.markdown(f"[Visit Subreddit]({info['url']})")
                    
                    st.markdown(f"**Title:** {info['title']}")
                    st.markdown(f"**Description:** {info['description']}")
            else:
                st.error(f"❌ {error_msg}")
    
    # Save configuration
    if save_btn:
        with st.spinner("Saving configuration..."):
            success = update_reddit_extraction_config(subreddit, time_filter, limit)
            
            if success:
                st.success("✅ Configuration saved successfully!")
                st.balloons()
                st.info("The new configuration will be used on the next pipeline run.")
            else:
                st.error("❌ Failed to save configuration. Please check file permissions.")
    
    # Show current configuration
    st.markdown("---")
    st.markdown("## 📄 Current Configuration File")
    
    with st.expander("View Full Configuration"):
        try:
            config_path = pathlib.Path(__file__).parent / "airflow" / "extraction" / "configuration.conf"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_content = f.read()
                st.code(config_content, language="ini")
            else:
                st.error("Configuration file not found")
        except Exception as e:
            st.error(f"Error reading configuration file: {e}")

# ============================================================================
# DATA VIEWER PAGE
# ============================================================================
elif page == "📊 Data Viewer":
    st.markdown('<h1 class="main-header">📊 Data Viewer</h1>', unsafe_allow_html=True)
    
    st.markdown("Browse, search, and export Reddit posts data.")
    
    # Data source selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        data_source = st.radio(
            "Data Source",
            options=["Local CSV Files", "Redshift Database"],
            horizontal=True
        )
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Load data
    @st.cache_data(ttl=300)
    def load_cached_data(prefer_redshift):
        return load_data(prefer_redshift=prefer_redshift)
    
    with st.spinner("Loading data..."):
        df = load_cached_data(prefer_redshift=(data_source == "Redshift Database"))
    
    if df is None or df.empty:
        st.warning("⚠️ No data available. Please run the pipeline first or check your data source.")
    else:
        # Data summary
        summary = get_data_summary(df)
        
        st.markdown("### 📊 Data Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Posts", f"{summary['total_posts']:,}")
        
        with col2:
            st.metric("Avg Score", f"{summary['avg_score']:.1f}")
        
        with col3:
            st.metric("Avg Comments", f"{summary['avg_comments']:.1f}")
        
        with col4:
            st.metric("Unique Authors", f"{summary['unique_authors']:,}")
        
        with col5:
            st.metric("NSFW Posts", f"{summary['nsfw_count']:,}")
        
        # Filters
        st.markdown("### 🔍 Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔎 Search in titles", "")
        
        with col2:
            min_score = st.number_input("Minimum Score", min_value=0, value=0)
        
        with col3:
            min_comments = st.number_input("Minimum Comments", min_value=0, value=0)
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_term:
            filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]
        
        if min_score > 0:
            filtered_df = filtered_df[filtered_df['score'] >= min_score]
        
        if min_comments > 0:
            filtered_df = filtered_df[filtered_df['num_comments'] >= min_comments]
        
        st.info(f"Showing {len(filtered_df)} of {len(df)} posts")
        
        # Display data
        st.markdown("### 📋 Posts Table")
        
        # Select columns to display
        display_columns = ['title', 'score', 'num_comments', 'author', 'created_utc', 'upvote_ratio', 'url']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        # Format the dataframe
        display_df = filtered_df[available_columns].copy()
        
        if 'created_utc' in display_df.columns:
            display_df['created_utc'] = pd.to_datetime(display_df['created_utc']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display with custom configuration
        st.dataframe(
            display_df,
            use_container_width=True,
            height=500,
            column_config={
                "title": st.column_config.TextColumn("Title", width="large"),
                "score": st.column_config.NumberColumn("Score", format="%d"),
                "num_comments": st.column_config.NumberColumn("Comments", format="%d"),
                "author": st.column_config.TextColumn("Author", width="small"),
                "created_utc": st.column_config.TextColumn("Posted", width="small"),
                "upvote_ratio": st.column_config.NumberColumn("Upvote Ratio", format="%.2f"),
                "url": st.column_config.LinkColumn("Link", width="small")
            }
        )
        
        # Export functionality
        st.markdown("### 💾 Export Data")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            export_filename = st.text_input(
                "Export Filename",
                value=f"reddit_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        
        with col2:
            if st.button("📥 Export to CSV", use_container_width=True):
                if export_to_csv(filtered_df, export_filename):
                    st.success(f"✅ Data exported to {export_filename}")
                else:
                    st.error("❌ Failed to export data")

# ============================================================================
# ANALYTICS DASHBOARD PAGE
# ============================================================================
elif page == "📈 Analytics Dashboard":
    st.markdown('<h1 class="main-header">📈 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("Explore trends, engagement metrics, and insights from Reddit data.")
    
    # Load data
    @st.cache_data(ttl=300)
    def load_cached_data_analytics():
        return load_data(prefer_redshift=False)
    
    with st.spinner("Loading data..."):
        df = load_cached_data_analytics()
    
    if df is None or df.empty:
        st.warning("⚠️ No data available for analysis. Please run the pipeline first.")
    else:
        # Overview metrics
        summary = get_data_summary(df)
        
        st.markdown("## 📊 Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Posts",
                f"{summary['total_posts']:,}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Total Engagement",
                f"{summary['total_score'] + summary['total_comments']:,}",
                delta=None
            )
        
        with col3:
            st.metric(
                "Avg Score per Post",
                f"{summary['avg_score']:.1f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Avg Comments per Post",
                f"{summary['avg_comments']:.1f}",
                delta=None
            )
        
        # Time series analysis
        st.markdown("## 📅 Time Series Analysis")
        
        tab1, tab2 = st.tabs(["Score Over Time", "Comments Over Time"])
        
        with tab1:
            fig_score = create_time_series_chart(df, metric='score')
            st.plotly_chart(fig_score, use_container_width=True)
        
        with tab2:
            fig_comments = create_time_series_chart(df, metric='num_comments')
            st.plotly_chart(fig_comments, use_container_width=True)
        
        # Top posts and authors
        st.markdown("## 🏆 Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Top Posts by Score")
            n_posts = st.slider("Number of posts to show", 5, 20, 10, key="top_posts_score")
            fig_top_posts = create_top_posts_chart(df, n=n_posts, metric='score')
            st.plotly_chart(fig_top_posts, use_container_width=True)
        
        with col2:
            st.markdown("### Top Posts by Comments")
            n_posts_comments = st.slider("Number of posts to show", 5, 20, 10, key="top_posts_comments")
            fig_top_comments = create_top_posts_chart(df, n=n_posts_comments, metric='num_comments')
            st.plotly_chart(fig_top_comments, use_container_width=True)
        
        # Author analysis
        st.markdown("## 👥 Author Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            n_authors = st.slider("Number of authors to show", 5, 20, 10)
            fig_authors = create_author_chart(df, n=n_authors)
            st.plotly_chart(fig_authors, use_container_width=True)
        
        with col2:
            st.markdown("### Engagement Scatter")
            fig_scatter = create_engagement_scatter(df)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Content analysis
        st.markdown("## 📝 Content Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Title Word Cloud")
            wordcloud_img = generate_wordcloud(df, column='title')
            if wordcloud_img:
                st.image(wordcloud_img, use_container_width=True)
            else:
                st.info("Unable to generate word cloud")
        
        with col2:
            st.markdown("### Content Metrics")
            
            if 'over_18' in df.columns:
                nsfw_counts = df['over_18'].value_counts()
                fig_nsfw = create_pie_chart(df, 'over_18', 'NSFW vs SFW Posts')
                st.plotly_chart(fig_nsfw, use_container_width=True)
        
        # Activity heatmap
        st.markdown("## 🔥 Activity Patterns")
        
        fig_heatmap = create_heatmap(df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Distribution analysis
        st.markdown("## 📊 Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_score_dist = create_distribution_chart(df, 'score')
            st.plotly_chart(fig_score_dist, use_container_width=True)
        
        with col2:
            fig_comments_dist = create_distribution_chart(df, 'num_comments')
            st.plotly_chart(fig_comments_dist, use_container_width=True)

# ============================================================================
# PIPELINE CONTROL PAGE
# ============================================================================
elif page == "🔧 Pipeline Control":
    st.markdown('<h1 class="main-header">🔧 Pipeline Control</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Monitor and control the Reddit data extraction pipeline.
    """)
    
    # Pipeline status
    st.markdown("## 📊 Pipeline Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Pipeline Type:** Airflow DAG  
        **Schedule:** Every 10 minutes (configurable)  
        **Location:** `/airflow/dags/elt_reddit_pipeline.py`
        """)
    
    with col2:
        current_config = get_reddit_extraction_config()
        st.success(f"""
        **Current Subreddit:** r/{current_config['subreddit']}  
        **Time Filter:** {current_config['time_filter']}  
        **Post Limit:** {current_config['limit'] if current_config['limit'] else 'No limit'}
        """)
    
    # Manual execution info
    st.markdown("## 🚀 Manual Execution")
    
    st.warning("""
    ⚠️ **Note:** This UI does not directly trigger the Airflow pipeline. To manually run the pipeline:
    
    1. Access your Airflow web UI (usually at `http://localhost:8080`)
    2. Find the DAG named `elt_reddit_pipeline`
    3. Click the "Trigger DAG" button
    
    Alternatively, you can run the extraction script manually:
    """)
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    st.code(f"""
# Navigate to the extraction directory
cd airflow/extraction

# Run the extraction script
python extract_reddit_etl.py {current_date}

# Upload to S3
python upload_aws_s3_etl.py {current_date}

# Copy to Redshift
python upload_aws_redshift_etl.py {current_date}
    """, language="bash")
    
    # Logs viewer
    st.markdown("## 📋 Recent Logs")
    
    st.info("Log viewing functionality requires Airflow API integration. Check Airflow UI for detailed logs.")
    
    # Data freshness
    st.markdown("## 🕐 Data Freshness")
    
    df = load_data(prefer_redshift=False)
    
    if df is not None and not df.empty and 'created_utc' in df.columns:
        latest_post = pd.to_datetime(df['created_utc']).max()
        oldest_post = pd.to_datetime(df['created_utc']).min()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Latest Post", latest_post.strftime("%Y-%m-%d %H:%M"))
        
        with col2:
            st.metric("Oldest Post", oldest_post.strftime("%Y-%m-%d %H:%M"))
        
        with col3:
            days_range = (latest_post - oldest_post).days
            st.metric("Data Range", f"{days_range} days")
    else:
        st.warning("No data available to check freshness")
    
    # Configuration check
    st.markdown("## ✅ Configuration Check")
    
    is_valid, errors = validate_config()
    
    if is_valid:
        st.success("✅ All configuration checks passed!")
    else:
        st.error("❌ Configuration issues detected:")
        for error in errors:
            st.write(f"- {error}")
    
    # AWS connection test
    st.markdown("## 🔌 Connection Tests")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Reddit API", use_container_width=True):
            with st.spinner("Testing Reddit API..."):
                is_valid, error_msg = test_reddit_credentials()
                if is_valid:
                    st.success("✅ Reddit API connection successful!")
                else:
                    st.error(f"❌ {error_msg}")
    
    with col2:
        if st.button("Test AWS Configuration", use_container_width=True):
            with st.spinner("Checking AWS configuration..."):
                aws_config = get_aws_config()
                if aws_config:
                    st.success("✅ AWS configuration loaded successfully!")
                    with st.expander("View AWS Config"):
                        st.json({k: v for k, v in aws_config.items() if 'password' not in k.lower()})
                else:
                    st.error("❌ Failed to load AWS configuration")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Reddit Analytics Integration Platform | Built with Streamlit</p>
    <p>Configure • Extract • Analyze • Visualize</p>
</div>
""", unsafe_allow_html=True)
