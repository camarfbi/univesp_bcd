# playlist/playlist_items.py
def get_playlist_items(youtube, playlist_id, next_page_token=None):
    res = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=5,
        pageToken=next_page_token
    ).execute()
    
    return res
