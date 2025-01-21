import os
from dotenv import load_dotenv
import pandas as pd
import snowflake.connector
import sys

# Load environment variables
load_dotenv()

# Function to query Snowflake
def query_snowflake(start_date, end_date):
    # Extract credentials from environment variables
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    account = os.getenv('ACCOUNT')
    warehouse = os.getenv('WAREHOUSE')
    database = os.getenv('DATABASE')
    schema = os.getenv('SCHEMA')

    # Logging the start of the connection process
    print(f"Attempting to connect to Snowflake with user: {user} and account: {account}")

    # Establish connection to Snowflake
    try:
        ctx = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        print("Successfully connected to Snowflake.")
    except Exception as e:
        print("Failed to connect to Snowflake:", e)
        sys.exit(1)

    # Create a cursor object
    cs = ctx.cursor()

    # Execute SQL query
    try:
        query = f"""
        SELECT 
        col1,
        col2,
        ...
        WHERE 
        DATE(col_date) BETWEEN '{start_date}' AND '{end_date}'
        """
        print(f"Executing query from {start_date} to {end_date}")
        cs.execute(query)

        # Fetch the result set from the cursor and deliver it as the Pandas DataFrame
        df = pd.DataFrame.from_records(iter(cs), columns=[x[0] for x in cs.description])

        # Convert all columns to string format to ensure compatibility with R Shiny
        df = df.astype(str)

        print("Query executed successfully.")
        # Convert the DataFrame to a dictionary of lists before returning
        return df.to_dict('list')
    except Exception as e:
        print("Failed to execute query:", e)
        sys.exit(1)
    finally:
        cs.close()
        ctx.close()
        print("Snowflake connection closed.")

# Function to query Snowflake for a sample
def query_snowflake_sample(start_date, end_date):
    # Reuse the connection setup from query_snowflake
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    account = os.getenv('ACCOUNT')
    warehouse = os.getenv('WAREHOUSE')
    database = os.getenv('DATABASE')
    schema = os.getenv('SCHEMA')

    print(f"Attempting to connect to Snowflake for a sample query with user: {user} and account: {account}")

    try:
        ctx = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        print("Successfully connected to Snowflake for sample query.")
    except Exception as e:
        print("Failed to connect to Snowflake for sample query:", e)
        sys.exit(1)

    cs = ctx.cursor()

    try:
        # Modify the original query to fetch only the top 10 rows
        query = f"""
        SELECT * FROM (
        SELECT 
        col1,
        col2,
        ...
        WHERE 
        DATE(col_date) BETWEEN '{start_date}' AND '{end_date}'
        ) LIMIT 10
        """
        print(f"Executing sample query from {start_date} to {end_date}")
        cs.execute(query)

        df = pd.DataFrame.from_records(iter(cs), columns=[x[0] for x in cs.description])
        df = df.astype(str)

        print("Sample query executed successfully.")
        return df.to_dict('list')
    except Exception as e:
        print("Failed to execute sample query:", e)
        sys.exit(1)
    finally:
        cs.close()
        ctx.close()
        print("Snowflake connection for sample query closed.")