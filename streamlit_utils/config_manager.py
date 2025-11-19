"""
Configuration management utilities for Reddit Analytics Pipeline
Handles reading and writing to configuration.conf file
"""

import configparser
import pathlib
from typing import Dict, Any, Optional


def get_config_path() -> pathlib.Path:
    """Get the path to the configuration file"""
    script_path = pathlib.Path(__file__).parent.parent.resolve()
    return script_path / "airflow" / "extraction" / "configuration.conf"


def read_config() -> configparser.ConfigParser:
    """
    Read the configuration file and return ConfigParser object
    
    Returns:
        ConfigParser object with all configuration sections
    """
    parser = configparser.ConfigParser()
    config_path = get_config_path()
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    parser.read(config_path)
    return parser


def write_config(parser: configparser.ConfigParser) -> bool:
    """
    Write the configuration back to file
    
    Args:
        parser: ConfigParser object to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config_path = get_config_path()
        with open(config_path, 'w') as configfile:
            parser.write(configfile)
        return True
    except Exception as e:
        print(f"Error writing configuration: {e}")
        return False


def get_reddit_extraction_config() -> Dict[str, Any]:
    """
    Get Reddit extraction configuration as a dictionary
    
    Returns:
        Dictionary with subreddit, time_filter, and limit
    """
    parser = read_config()
    
    if not parser.has_section("reddit_extraction"):
        # Return defaults if section doesn't exist
        return {
            "subreddit": "dataengineering",
            "time_filter": "day",
            "limit": None
        }
    
    limit_value = parser.get("reddit_extraction", "limit")
    
    return {
        "subreddit": parser.get("reddit_extraction", "subreddit"),
        "time_filter": parser.get("reddit_extraction", "time_filter"),
        "limit": None if limit_value == "None" else int(limit_value)
    }


def update_reddit_extraction_config(subreddit: str, time_filter: str, limit: Optional[int]) -> bool:
    """
    Update Reddit extraction configuration
    
    Args:
        subreddit: Name of the subreddit to extract from
        time_filter: Time filter (day, week, month, year, all)
        limit: Maximum number of posts to extract (None for no limit)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        parser = read_config()
        
        # Create section if it doesn't exist
        if not parser.has_section("reddit_extraction"):
            parser.add_section("reddit_extraction")
        
        # Update values
        parser.set("reddit_extraction", "subreddit", subreddit)
        parser.set("reddit_extraction", "time_filter", time_filter)
        parser.set("reddit_extraction", "limit", "None" if limit is None else str(limit))
        
        return write_config(parser)
    except Exception as e:
        print(f"Error updating configuration: {e}")
        return False


def get_aws_config() -> Dict[str, str]:
    """
    Get AWS configuration as a dictionary
    
    Returns:
        Dictionary with AWS configuration values
    """
    parser = read_config()
    
    if not parser.has_section("aws_config"):
        return {}
    
    return {
        "bucket_name": parser.get("aws_config", "bucket_name"),
        "redshift_username": parser.get("aws_config", "redshift_username"),
        "redshift_password": parser.get("aws_config", "redshift_password"),
        "redshift_hostname": parser.get("aws_config", "redshift_hostname"),
        "redshift_role": parser.get("aws_config", "redshift_role"),
        "redshift_port": parser.get("aws_config", "redshift_port"),
        "redshift_database": parser.get("aws_config", "redshift_database"),
        "account_id": parser.get("aws_config", "account_id"),
        "aws_region": parser.get("aws_config", "aws_region"),
    }


def get_reddit_api_config() -> Dict[str, str]:
    """
    Get Reddit API configuration as a dictionary
    
    Returns:
        Dictionary with Reddit API credentials
    """
    parser = read_config()
    
    if not parser.has_section("reddit_config"):
        return {}
    
    return {
        "secret": parser.get("reddit_config", "secret"),
        "client_id": parser.get("reddit_config", "client_id"),
        "developer": parser.get("reddit_config", "developer"),
        "name": parser.get("reddit_config", "name"),
    }


def validate_config() -> tuple[bool, list[str]]:
    """
    Validate that all required configuration sections and keys exist
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        parser = read_config()
    except FileNotFoundError as e:
        return False, [str(e)]
    
    # Check required sections
    required_sections = ["aws_config", "reddit_config", "reddit_extraction"]
    for section in required_sections:
        if not parser.has_section(section):
            errors.append(f"Missing required section: [{section}]")
    
    # Check required keys in aws_config
    if parser.has_section("aws_config"):
        required_aws_keys = ["bucket_name", "redshift_username", "redshift_password", 
                            "redshift_hostname", "redshift_database"]
        for key in required_aws_keys:
            if not parser.has_option("aws_config", key):
                errors.append(f"Missing required key in [aws_config]: {key}")
    
    # Check required keys in reddit_config
    if parser.has_section("reddit_config"):
        required_reddit_keys = ["secret", "client_id"]
        for key in required_reddit_keys:
            if not parser.has_option("reddit_config", key):
                errors.append(f"Missing required key in [reddit_config]: {key}")
    
    # Check required keys in reddit_extraction
    if parser.has_section("reddit_extraction"):
        required_extraction_keys = ["subreddit", "time_filter", "limit"]
        for key in required_extraction_keys:
            if not parser.has_option("reddit_extraction", key):
                errors.append(f"Missing required key in [reddit_extraction]: {key}")
    
    return len(errors) == 0, errors
