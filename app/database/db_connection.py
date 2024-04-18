# database/db_connection.py
import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import psycopg2

def create_connection():
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    PLAYLIST_ID = os.environ.get('PLAYLIST_ID')

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    return conn
