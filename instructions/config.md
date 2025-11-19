
# Configuration

Next, you'll need to create a configuration file with your details. The extract and load scripts in our pipeline will utilise the details here.

## Setup

1. Create a configuration file under `~/Reddit-API-Pipeline/airflow/extraction/` called `configuration.conf`:

    ```bash
    touch ~/Reddit-API-Pipeline/airflow/extraction/configuration.conf
    ```

1. Copy in the following:

    ```conf
    [aws_config]
    bucket_name = XXXXX
    redshift_username = awsuser
    redshift_password = XXXXX
    redshift_hostname =  XXXXX
    redshift_role = RedShiftLoadRole
    redshift_port = 5439
    redshift_database = dev
    account_id = 
    aws_region = us-east-1

    [reddit_config]
    secret = XXXXX
    developer = XXXXX
    name = XXXXX
    client_id = XXXXX

    [reddit_extraction]
    subreddit = dataengineering
    time_filter = day
    limit = None
    ```


1. Change `XXXXX` values

    * If you need a reminder of your `aws_config` details, change folder back into the terraform folder and run the command. It will output the values you need to store under `aws_config`. Just be sure to remove any `"` from the strings.

        ```bash
        terraform output
        ```
        
    * For `reddit_config` these are the details you took note of after setting up your Reddit App. Note the `developer` is your Reddit name.

    * For `reddit_extraction`:
        - `subreddit`: The name of the subreddit to extract from (without 'r/' prefix). Default is `dataengineering`. You can change this to any public subreddit.
        - `time_filter`: Time period for top posts (`hour`, `day`, `week`, `month`, `year`, `all`). Default is `day`.
        - `limit`: Maximum number of posts to extract. Use `None` for no limit, or a number like `100` for a specific limit.

> **Tip**: You can also configure the subreddit using the Streamlit UI instead of manually editing this file. See [Streamlit UI Guide](streamlit_ui.md) for details.

---

[Previous Step](setup_infrastructure.md) | [Next Step](docker_airflow.md)

or

[Back to main README](../README.md)
