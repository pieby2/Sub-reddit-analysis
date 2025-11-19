"""
Data loading utilities for Reddit Analytics Pipeline
Handles loading data from Redshift, S3, and local CSV files
"""

import pandas as pd
import psycopg2
from psycopg2 import sql
import pathlib
from typing import Optional
from .config_manager import get_aws_config


def load_from_redshift(table_name: str = "reddit") -> Optional[pd.DataFrame]:
    """
    Load data from Redshift table
    
    Args:
        table_name: Name of the Redshift table
        
    Returns:
        DataFrame with Reddit data or None if error
    """
    try:
        config = get_aws_config()
        
        # Connect to Redshift
        conn = psycopg2.connect(
            dbname=config["redshift_database"],
            user=config["redshift_username"],
            password=config["redshift_password"],
            host=config["redshift_hostname"],
            port=config["redshift_port"]
        )
        
        # Query data
        query = sql.SQL("SELECT * FROM {table} ORDER BY created_utc DESC;").format(
            table=sql.Identifier(table_name)
        )
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error loading from Redshift: {e}")
        return None


def load_local_data(data_dir: str = "/tmp") -> Optional[pd.DataFrame]:
    """
    Load data from local CSV files
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        DataFrame with combined data from all CSV files or None if error
    """
    try:
        data_path = pathlib.Path(data_dir)
        
        # Find all CSV files
        csv_files = list(data_path.glob("*.csv"))
        
        if not csv_files:
            # Try the airflow extraction directory as fallback
            script_path = pathlib.Path(__file__).parent.parent.resolve()
            alt_path = script_path / "airflow" / "extraction"
            csv_files = list(alt_path.glob("*.csv"))
        
        if not csv_files:
            return None
        
        # Load and combine all CSV files
        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
                continue
        
        if not dfs:
            return None
        
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Remove duplicates based on post ID
        if 'id' in combined_df.columns:
            combined_df = combined_df.drop_duplicates(subset=['id'], keep='last')
        
        # Convert created_utc to datetime if it's not already
        if 'created_utc' in combined_df.columns:
            combined_df['created_utc'] = pd.to_datetime(combined_df['created_utc'])
        
        # Sort by date
        if 'created_utc' in combined_df.columns:
            combined_df = combined_df.sort_values('created_utc', ascending=False)
        
        return combined_df
        
    except Exception as e:
        print(f"Error loading local data: {e}")
        return None


def load_data(prefer_redshift: bool = True) -> Optional[pd.DataFrame]:
    """
    Load data from available source (Redshift or local CSV)
    
    Args:
        prefer_redshift: If True, try Redshift first, then fall back to local
        
    Returns:
        DataFrame with Reddit data or None if no data available
    """
    if prefer_redshift:
        # Try Redshift first
        df = load_from_redshift()
        if df is not None and not df.empty:
            return df
        
        # Fall back to local
        return load_local_data()
    else:
        # Try local first
        df = load_local_data()
        if df is not None and not df.empty:
            return df
        
        # Fall back to Redshift
        return load_from_redshift()


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Get summary statistics for the data
    
    Args:
        df: DataFrame with Reddit data
        
    Returns:
        Dictionary with summary statistics
    """
    if df is None or df.empty:
        return {}
    
    summary = {
        "total_posts": len(df),
        "date_range": {
            "start": df['created_utc'].min() if 'created_utc' in df.columns else None,
            "end": df['created_utc'].max() if 'created_utc' in df.columns else None
        },
        "total_score": df['score'].sum() if 'score' in df.columns else 0,
        "total_comments": df['num_comments'].sum() if 'num_comments' in df.columns else 0,
        "avg_score": df['score'].mean() if 'score' in df.columns else 0,
        "avg_comments": df['num_comments'].mean() if 'num_comments' in df.columns else 0,
        "unique_authors": df['author'].nunique() if 'author' in df.columns else 0,
        "nsfw_count": df['over_18'].sum() if 'over_18' in df.columns else 0,
        "edited_count": df['edited'].sum() if 'edited' in df.columns else 0,
    }
    
    return summary


def export_to_csv(df: pd.DataFrame, filename: str) -> bool:
    """
    Export DataFrame to CSV file
    
    Args:
        df: DataFrame to export
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        df.to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False
