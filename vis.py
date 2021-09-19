import sqlite3
import pandas as pd
import plotly.express as px
from geoip import runapi


def parsedb(file):
    """
    This function parses the database file and returns pandas DF
    """
    conn = sqlite3.connect(file)
    df = pd.read_sql_query("SELECT * FROM andrewafs", conn)
    return df

def truncatedate(df):
    """
    truncate date column to nearest day
    """
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    return df

def collatedate(df):
    """
    collate data by date, return a dictionary
    """
    df = df.groupby(['date']).agg(list)
    return df

def unique(df):
    """
    drop duplicate rows
    """
    df = df.drop_duplicates()
    return df

df = parsedb("/Users/elizabethxu/Desktop/TODO/andrewafs.db")
df = truncatedate(df)
df = unique(df)
df = collatedate(df)

allips = df['ipaddr'].tolist()
flattened_ips = [item for sublist in allips for item in sublist]
unique_ips = list(set(flattened_ips))

runapi(unique_ips)

breakpoint()