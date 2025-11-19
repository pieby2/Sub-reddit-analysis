# Reddit Analytics Integration Platform

> **A modern, configurable data pipeline for analyzing any Reddit subreddit with an interactive dashboard**

Extract, transform, and visualize Reddit data from any subreddit using a production-grade ETL pipeline with cloud storage, automated orchestration, and an interactive Streamlit UI.

---

## ✨ Key Features

- 🎯 **Configurable Subreddit Analysis** - Analyze any public subreddit, not just one
- 📊 **Interactive Streamlit Dashboard** - Modern web UI for configuration and visualization
- ☁️ **Cloud-Native Architecture** - AWS S3 for storage, Redshift for data warehousing
- 🔄 **Automated Orchestration** - Airflow DAGs running in Docker containers
- 📈 **Rich Analytics** - Time series, engagement metrics, word clouds, heatmaps, and more
- 🛠️ **Infrastructure as Code** - Terraform for reproducible AWS resource management
- 🔍 **Data Transformation** - dbt for clean, tested data models

---

## 🚀 Quick Start

### Option 1: Use the Streamlit Dashboard (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/AnMol12499/Reddit-Analytics-Integration-Platform.git
cd Reddit-Analytics-Integration-Platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your credentials (see Configuration section below)
# Edit airflow/extraction/configuration.conf

# 4. Launch the Streamlit dashboard
streamlit run streamlit_app.py
```

The dashboard will open at `http://localhost:8501` where you can:
- Configure which subreddit to analyze
- View extracted data in an interactive table
- Explore analytics with 10+ visualizations
- Monitor pipeline status

### Option 2: Full Pipeline Setup

For the complete ETL pipeline with Airflow, AWS, and dbt, follow the [detailed setup guide](#setup).

---

## 📊 Streamlit Dashboard

The interactive dashboard provides a user-friendly interface for the entire pipeline:

### 🏠 Home Page
- System status checks (configuration, Reddit API, data availability)
- Quick statistics overview
- Getting started guide

### ⚙️ Configuration Manager
- Change target subreddit with validation
- Configure time filter (hour, day, week, month, year, all)
- Set post extraction limits
- View subreddit information (subscribers, description)
- Save settings to configuration file

### 📊 Data Viewer
- Browse all extracted posts in an interactive table
- Search posts by title
- Filter by score or comment count
- View post details (author, date, upvote ratio, URL)
- Export filtered data to CSV

### 📈 Analytics Dashboard

**Overview Metrics:**
- Total posts, engagement, average scores, unique authors

**Visualizations:**
- 📅 **Time Series**: Score and comments over time
- 🏆 **Top Posts**: Highest scoring and most discussed posts
- 👥 **Author Analytics**: Most active contributors
- 💬 **Engagement Analysis**: Score vs comments scatter plot
- ☁️ **Word Clouds**: Popular terms from post titles
- 🔥 **Activity Heatmap**: Posting patterns by day and hour
- 📊 **Distributions**: Score and comment histograms
- 🥧 **Content Breakdown**: NSFW ratio, edited posts

### 🔧 Pipeline Control
- View current pipeline configuration
- Monitor data freshness
- Test Reddit API and AWS connections
- Manual execution instructions

**Screenshot:**

<img src="images/GDS-Dashboard.png" width=70% height=70%>

---

## 🏗️ Architecture

<img src="images/workflow.png" width=70% height=70%>

### Pipeline Flow

1. **Configure** - Set target subreddit via Streamlit UI or config file
2. **Extract** - Pull data from [Reddit API](https://www.reddit.com/dev/api/) using PRAW
3. **Load** - Upload raw data to [AWS S3](https://aws.amazon.com/s3/)
4. **Copy** - Transfer data to [AWS Redshift](https://aws.amazon.com/redshift/) data warehouse
5. **Transform** - Clean and model data using [dbt](https://www.getdbt.com)
6. **Visualize** - Interactive [Streamlit](https://streamlit.io) dashboard
7. **Report** - Optional [PowerBI](https://powerbi.microsoft.com/en-gb/) or [Google Data Studio](https://datastudio.google.com) dashboards
8. **Orchestrate** - Automated scheduling with [Airflow](https://airflow.apache.org) in [Docker](https://www.docker.com)
9. **Provision** - Infrastructure managed by [Terraform](https://www.terraform.io)

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Data Extraction** | Python, PRAW (Reddit API) |
| **Storage** | AWS S3 |
| **Data Warehouse** | AWS Redshift |
| **Transformation** | dbt |
| **Orchestration** | Apache Airflow |
| **Containerization** | Docker |
| **Infrastructure** | Terraform |
| **Visualization** | Streamlit, Plotly, WordCloud |
| **Optional BI** | PowerBI, Google Data Studio |

---

## ⚙️ Configuration

The pipeline is configured via `airflow/extraction/configuration.conf`:

```ini
[reddit_config]
secret = YOUR_REDDIT_SECRET
client_id = YOUR_REDDIT_CLIENT_ID
developer = YOUR_REDDIT_USERNAME
name = YOUR_APP_NAME

[aws_config]
bucket_name = your-s3-bucket
redshift_username = awsuser
redshift_password = your-password
redshift_hostname = your-redshift-endpoint
# ... other AWS settings

[reddit_extraction]
subreddit = dataengineering    # Change to any subreddit
time_filter = day              # hour, day, week, month, year, all
limit = None                   # None for no limit, or a number
```

**Tip:** Use the Streamlit UI Configuration Manager to edit these settings with validation!

---

## � Setup

### Prerequisites

- Python 3.7+
- Docker & Docker Compose
- AWS Account (free tier eligible)
- Reddit API credentials

### Full Pipeline Installation

Follow these steps for the complete setup:

1. **[Overview](instructions/overview.md)** - Project overview and architecture
2. **[Reddit API Configuration](instructions/reddit.md)** - Create Reddit app and get credentials
3. **[AWS Account](instructions/aws.md)** - Set up AWS account
4. **[Infrastructure with Terraform](instructions/setup_infrastructure.md)** - Provision AWS resources
5. **[Configuration Details](instructions/config.md)** - Configure the pipeline
6. **[Docker & Airflow](instructions/docker_airflow.md)** - Set up orchestration
7. **[Streamlit UI](instructions/streamlit_ui.md)** - Run the dashboard
8. **[dbt](instructions/dbt.md)** - Data transformation (optional)
9. **[Dashboard](instructions/visualisation.md)** - BI tools integration (optional)
10. **[Final Notes & Termination](instructions/terminate.md)** - Cleanup and shutdown
11. **[Improvements](instructions/improvements.md)** - Future enhancements

### Quick Install (Dashboard Only)

To use just the Streamlit dashboard without the full pipeline:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Reddit API credentials
# Edit airflow/extraction/configuration.conf

# Run the dashboard
streamlit run streamlit_app.py
```

---

## 💡 Usage Examples

### Analyze a Different Subreddit

**Via Streamlit UI:**
1. Open the dashboard: `streamlit run streamlit_app.py`
2. Go to "⚙️ Configuration" page
3. Enter subreddit name (e.g., "python", "machinelearning")
4. Click "🔍 Validate Subreddit"
5. Click "💾 Save Configuration"
6. Run the pipeline (via Airflow or manually)

**Via Configuration File:**
```bash
# Edit configuration
nano airflow/extraction/configuration.conf

# Change the subreddit line:
subreddit = python

# Run extraction manually
cd airflow/extraction
python extract_reddit_etl.py 20250120
```

### View Analytics

```bash
# Launch dashboard
streamlit run streamlit_app.py

# Navigate to "📈 Analytics Dashboard" page
# Explore interactive visualizations
```

---

## 📁 Project Structure

```
Reddit-Analytics-Integration-Platform/
├── airflow/
│   ├── dags/                    # Airflow DAG definitions
│   ├── extraction/              # Data extraction scripts
│   │   ├── configuration.conf   # Pipeline configuration
│   │   ├── extract_reddit_etl.py
│   │   ├── upload_aws_s3_etl.py
│   │   └── upload_aws_redshift_etl.py
│   └── docker-compose.yaml      # Airflow Docker setup
├── streamlit_utils/             # Streamlit utility modules
│   ├── config_manager.py        # Configuration management
│   ├── data_loader.py           # Data loading from Redshift/CSV
│   ├── reddit_api.py            # Reddit API utilities
│   └── visualizations.py        # Chart generation
├── terraform/                   # Infrastructure as Code
├── instructions/                # Detailed setup guides
├── streamlit_app.py            # Main Streamlit dashboard
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🎯 Use Cases

- **Subreddit Analysis**: Understand posting patterns, engagement, and trends
- **Community Research**: Study different communities and their behaviors
- **Content Strategy**: Identify what content performs well
- **Trend Tracking**: Monitor topics and discussions over time
- **Data Engineering Practice**: Learn modern data pipeline techniques

---

## 🔒 Security Notes

> **⚠️ Important**: The `configuration.conf` file contains sensitive credentials. 
> - Never commit this file to version control
> - For production, use environment variables or AWS Secrets Manager
> - Ensure proper IAM roles and permissions for AWS resources

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new visualizations
- Improve error handling
- Add support for more data sources
- Enhance the Streamlit UI
- Optimize performance

---

## 📝 License

This project is for educational purposes. Please respect Reddit's API terms of service and rate limits.

---

## 🙏 Acknowledgments

- Built with modern data engineering best practices
- Inspired by the Data Engineering community
- Uses open-source tools and frameworks

---

## 📚 Additional Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [dbt Documentation](https://docs.getdbt.com/)
- [AWS Redshift Documentation](https://docs.aws.amazon.com/redshift/)

---


