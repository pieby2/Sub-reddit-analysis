# Streamlit UI Guide

## Overview

The Reddit Analytics Platform includes an interactive **Streamlit dashboard** that provides a user-friendly interface for configuring, monitoring, and visualizing your Reddit data pipeline.

## Installation

### Prerequisites

- Python 3.7 or higher
- All dependencies from `requirements.txt`

### Setup

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

This will install Streamlit and all required visualization libraries.

2. **Verify Installation**

```bash
streamlit --version
```

## Running the Application

### Start the Streamlit App

From the project root directory:

```bash
streamlit run streamlit_app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

### Custom Port

To run on a different port:

```bash
streamlit run streamlit_app.py --server.port 8502
```

## Features

### 🏠 Home Page

The home page provides an overview of your system status:

- **Configuration Status**: Validates that all required configuration sections exist
- **Reddit API Status**: Tests connection to Reddit API
- **Data Availability**: Checks if data has been extracted
- **Quick Statistics**: Shows summary metrics (total posts, score, comments, authors)

### ⚙️ Configuration Manager

Configure your Reddit extraction settings:

**Features:**
- Change target subreddit
- Set time filter (hour, day, week, month, year, all)
- Configure post limit (no limit or custom number)
- Validate subreddit exists before saving
- View subreddit information (subscribers, description)

**How to Use:**
1. Enter the subreddit name (without 'r/' prefix)
2. Select time filter and post limit
3. Click "🔍 Validate Subreddit" to check if it exists
4. Click "💾 Save Configuration" to apply changes
5. Changes will be used on the next pipeline run

### 📊 Data Viewer

Browse and explore extracted Reddit posts:

**Features:**
- Load data from Redshift or local CSV files
- Search posts by title
- Filter by minimum score or comments
- View detailed post information
- Export filtered data to CSV

**Columns Displayed:**
- Title
- Score (upvotes)
- Number of comments
- Author
- Posted date/time
- Upvote ratio
- Post URL (clickable link)

**Export:**
- Filter data as needed
- Enter export filename
- Click "📥 Export to CSV" to download

### 📈 Analytics Dashboard

Visualize trends and insights from your Reddit data:

**Overview Metrics:**
- Total posts
- Total engagement (score + comments)
- Average score per post
- Average comments per post

**Time Series Analysis:**
- Score over time
- Comments over time
- Interactive charts with zoom and pan

**Top Performers:**
- Top posts by score (configurable number)
- Top posts by comments
- Most active authors

**Engagement Analysis:**
- Scatter plot: Score vs Comments
- Color-coded by upvote ratio
- Hover to see post details

**Content Analysis:**
- Word cloud from post titles
- NSFW vs SFW distribution
- Edited posts ratio

**Activity Patterns:**
- Heatmap showing posting activity by day of week and hour
- Identify peak posting times

**Distribution Analysis:**
- Score distribution histogram
- Comments distribution histogram

### 🔧 Pipeline Control

Monitor and control your data pipeline:

**Features:**
- View current pipeline configuration
- Check data freshness (latest and oldest posts)
- Test Reddit API connection
- Test AWS configuration
- View manual execution instructions

**Connection Tests:**
- Test Reddit API credentials
- Verify AWS configuration loaded correctly

## Tips & Best Practices

### Performance

1. **Data Caching**: The app uses Streamlit's caching to improve performance. Data is cached for 5 minutes.
2. **Refresh Data**: Click the "🔄 Refresh Data" button to clear cache and reload
3. **Large Datasets**: For datasets with 1000+ posts, filtering is recommended for better performance

### Configuration

1. **Validate Before Saving**: Always validate a subreddit before saving to avoid pipeline errors
2. **Backup Config**: Keep a backup of `configuration.conf` before making changes
3. **Test with Small Limits**: When testing a new subreddit, use a small post limit first

### Data Sources

1. **Redshift vs Local**: 
   - Use Redshift for production data
   - Use Local CSV for testing or when Redshift is unavailable
2. **Data Freshness**: Check the Pipeline Control page to see when data was last updated

## Troubleshooting

### App Won't Start

**Error: `ModuleNotFoundError: No module named 'streamlit'`**

Solution:
```bash
pip install -r requirements.txt
```

**Error: `Configuration file not found`**

Solution: Ensure you're running the app from the project root directory where `airflow/extraction/configuration.conf` exists.

### Data Not Loading

**No data available**

Possible causes:
1. Pipeline hasn't run yet - run the Airflow DAG or extraction script manually
2. No CSV files in `/tmp` directory
3. Redshift connection issues - check AWS credentials

Solution:
- Run the pipeline manually (see Pipeline Control page for instructions)
- Check that CSV files exist in `/tmp` or extraction directory
- Verify AWS configuration in `configuration.conf`

### Reddit API Errors

**Error: `Unable to connect to Reddit API`**

Solution:
1. Check Reddit API credentials in `configuration.conf`
2. Verify `client_id` and `secret` are correct
3. Ensure you have a valid Reddit app created

### Visualization Issues

**Word cloud not generating**

Solution:
- Ensure there are posts with titles in the dataset
- Check that `wordcloud` package is installed: `pip install wordcloud`

**Charts not displaying**

Solution:
- Ensure `plotly` is installed: `pip install plotly`
- Clear browser cache and refresh

## Advanced Usage

### Custom Styling

The app includes custom CSS for styling. To modify:

1. Edit the CSS in `streamlit_app.py` under the `st.markdown()` section
2. Restart the app to see changes

### Adding Custom Pages

To add a new page:

1. Add a new option to the sidebar radio button
2. Create a new `elif` block for your page
3. Add your custom functionality

### Integration with Airflow

While the UI doesn't directly trigger Airflow DAGs, you can:

1. Use the Configuration Manager to set parameters
2. Manually trigger the DAG in Airflow UI
3. View results in the Analytics Dashboard

## Keyboard Shortcuts

- `Ctrl + R` or `Cmd + R`: Refresh the app
- `Ctrl + K` or `Cmd + K`: Clear cache and rerun

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the main README.md
3. Check Airflow logs for pipeline issues
4. Verify all configuration settings

---

**Next Steps:**
- [Configuration Setup](config.md)
- [Docker & Airflow](docker_airflow.md)
- [Back to main README](../README.md)
