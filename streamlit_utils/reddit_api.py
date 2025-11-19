"""
Reddit API utilities for validating subreddits and testing credentials
"""

import praw
from typing import Optional, Dict, Any
from .config_manager import get_reddit_api_config


def create_reddit_instance() -> Optional[praw.Reddit]:
    """
    Create a Reddit API instance using credentials from config
    
    Returns:
        Reddit instance or None if credentials are invalid
    """
    try:
        config = get_reddit_api_config()
        
        if not config.get("client_id") or not config.get("secret"):
            return None
        
        reddit = praw.Reddit(
            client_id=config["client_id"],
            client_secret=config["secret"],
            user_agent=f"Reddit Analytics by u/{config.get('developer', 'unknown')}"
        )
        
        # Test the connection
        reddit.user.me()
        
        return reddit
    except Exception as e:
        print(f"Error creating Reddit instance: {e}")
        return None


def validate_subreddit(subreddit_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a subreddit exists and is accessible
    
    Args:
        subreddit_name: Name of the subreddit to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        reddit = create_reddit_instance()
        
        if reddit is None:
            return False, "Unable to connect to Reddit API. Check your credentials."
        
        # Try to access the subreddit
        subreddit = reddit.subreddit(subreddit_name)
        
        # This will raise an exception if the subreddit doesn't exist
        _ = subreddit.display_name
        
        # Check if subreddit is private or banned
        try:
            _ = subreddit.subscribers
        except Exception:
            return False, f"Subreddit r/{subreddit_name} exists but may be private or restricted."
        
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "Redirect" in error_msg:
            return False, f"Subreddit r/{subreddit_name} does not exist."
        else:
            return False, f"Error validating subreddit: {error_msg}"


def get_subreddit_info(subreddit_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a subreddit
    
    Args:
        subreddit_name: Name of the subreddit
        
    Returns:
        Dictionary with subreddit info or None if error
    """
    try:
        reddit = create_reddit_instance()
        
        if reddit is None:
            return None
        
        subreddit = reddit.subreddit(subreddit_name)
        
        return {
            "name": subreddit.display_name,
            "title": subreddit.title,
            "description": subreddit.public_description,
            "subscribers": subreddit.subscribers,
            "created_utc": subreddit.created_utc,
            "over18": subreddit.over18,
            "url": f"https://reddit.com/r/{subreddit.display_name}"
        }
        
    except Exception as e:
        print(f"Error getting subreddit info: {e}")
        return None


def test_reddit_credentials() -> tuple[bool, Optional[str]]:
    """
    Test if Reddit API credentials are valid
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        reddit = create_reddit_instance()
        
        if reddit is None:
            return False, "Unable to create Reddit instance. Check your credentials in configuration.conf"
        
        # Try to access Reddit
        reddit.user.me()
        
        return True, None
        
    except Exception as e:
        return False, f"Reddit API credentials are invalid: {str(e)}"
