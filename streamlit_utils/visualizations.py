"""
Visualization utilities for Reddit Analytics Dashboard
Creates reusable chart components using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from wordcloud import WordCloud
import io
from PIL import Image
from typing import Optional


def create_time_series_chart(df: pd.DataFrame, metric: str = "score") -> go.Figure:
    """
    Create time series chart showing metric over time
    
    Args:
        df: DataFrame with Reddit data
        metric: Metric to plot (score, num_comments, etc.)
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty or 'created_utc' not in df.columns:
        return go.Figure()
    
    # Group by date
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['created_utc']).dt.date
    
    daily_data = df_copy.groupby('date').agg({
        metric: 'sum',
        'id': 'count'
    }).reset_index()
    
    daily_data.columns = ['date', metric, 'post_count']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data[metric],
        mode='lines+markers',
        name=metric.replace('_', ' ').title(),
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"{metric.replace('_', ' ').title()} Over Time",
        xaxis_title="Date",
        yaxis_title=metric.replace('_', ' ').title(),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_top_posts_chart(df: pd.DataFrame, n: int = 10, metric: str = "score") -> go.Figure:
    """
    Create bar chart showing top posts
    
    Args:
        df: DataFrame with Reddit data
        n: Number of top posts to show
        metric: Metric to sort by
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty:
        return go.Figure()
    
    # Get top posts
    top_posts = df.nlargest(n, metric)[['title', metric]].copy()
    
    # Truncate long titles
    top_posts['short_title'] = top_posts['title'].apply(
        lambda x: x[:50] + '...' if len(x) > 50 else x
    )
    
    fig = px.bar(
        top_posts,
        y='short_title',
        x=metric,
        orientation='h',
        title=f"Top {n} Posts by {metric.replace('_', ' ').title()}",
        labels={'short_title': 'Post Title', metric: metric.replace('_', ' ').title()},
        color=metric,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=max(400, n * 40),
        yaxis={'categoryorder': 'total ascending'},
        template='plotly_white'
    )
    
    return fig


def create_author_chart(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """
    Create bar chart showing most active authors
    
    Args:
        df: DataFrame with Reddit data
        n: Number of top authors to show
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty or 'author' not in df.columns:
        return go.Figure()
    
    # Count posts per author
    author_counts = df['author'].value_counts().head(n).reset_index()
    author_counts.columns = ['author', 'post_count']
    
    fig = px.bar(
        author_counts,
        x='author',
        y='post_count',
        title=f"Top {n} Most Active Authors",
        labels={'author': 'Author', 'post_count': 'Number of Posts'},
        color='post_count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        xaxis_tickangle=-45
    )
    
    return fig


def create_engagement_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot showing relationship between score and comments
    
    Args:
        df: DataFrame with Reddit data
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty:
        return go.Figure()
    
    fig = px.scatter(
        df,
        x='num_comments',
        y='score',
        hover_data=['title', 'author'],
        title="Post Engagement: Score vs Comments",
        labels={'num_comments': 'Number of Comments', 'score': 'Score'},
        opacity=0.6,
        color='upvote_ratio' if 'upvote_ratio' in df.columns else None,
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        height=500,
        template='plotly_white'
    )
    
    return fig


def create_distribution_chart(df: pd.DataFrame, column: str) -> go.Figure:
    """
    Create histogram showing distribution of a metric
    
    Args:
        df: DataFrame with Reddit data
        column: Column to create distribution for
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty or column not in df.columns:
        return go.Figure()
    
    fig = px.histogram(
        df,
        x=column,
        title=f"Distribution of {column.replace('_', ' ').title()}",
        labels={column: column.replace('_', ' ').title()},
        nbins=30,
        color_discrete_sequence=['#636EFA']
    )
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def create_pie_chart(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    """
    Create pie chart for categorical data
    
    Args:
        df: DataFrame with Reddit data
        column: Column to create pie chart for
        title: Chart title
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty or column not in df.columns:
        return go.Figure()
    
    value_counts = df[column].value_counts()
    
    fig = px.pie(
        values=value_counts.values,
        names=value_counts.index,
        title=title,
        hole=0.3
    )
    
    fig.update_layout(
        height=400,
        template='plotly_white'
    )
    
    return fig


def generate_wordcloud(df: pd.DataFrame, column: str = 'title') -> Optional[Image.Image]:
    """
    Generate word cloud from text data
    
    Args:
        df: DataFrame with Reddit data
        column: Column containing text data
        
    Returns:
        PIL Image or None if error
    """
    if df is None or df.empty or column not in df.columns:
        return None
    
    try:
        # Combine all text
        text = ' '.join(df[column].astype(str).tolist())
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(text)
        
        # Convert to PIL Image
        image = wordcloud.to_image()
        
        return image
        
    except Exception as e:
        print(f"Error generating word cloud: {e}")
        return None


def create_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create heatmap showing posting activity by day of week and hour
    
    Args:
        df: DataFrame with Reddit data
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty or 'created_utc' not in df.columns:
        return go.Figure()
    
    df_copy = df.copy()
    df_copy['created_utc'] = pd.to_datetime(df_copy['created_utc'])
    df_copy['day_of_week'] = df_copy['created_utc'].dt.day_name()
    df_copy['hour'] = df_copy['created_utc'].dt.hour
    
    # Create pivot table
    heatmap_data = df_copy.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
    
    # Reorder days
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex([d for d in days_order if d in heatmap_pivot.index])
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='YlOrRd',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Posting Activity Heatmap (Day vs Hour)",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=400,
        template='plotly_white'
    )
    
    return fig
