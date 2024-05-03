# youtube/youtube_client.py
from googleapiclient.discovery import build
import os

def create_youtube_client():
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    return youtube
