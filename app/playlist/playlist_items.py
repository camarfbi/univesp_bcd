# playlist/playlist_items.py
def get_playlist_items(youtube, playlist_id, next_page_token=None):
    res = youtube.playlistItems().list(
        part=['snippet', 'status'],
        playlistId=playlist_id,
        maxResults=5,
        pageToken=next_page_token
    ).execute()
    
    # Verificar se a resposta indica um erro de limite de consulta
    if 'error' in res:
        error_message = res['error']['message']
        if 'quota' in error_message.lower():
            print("Limite de consulta à API do YouTube excedido. Aguarde antes de tentar novamente.")
            return None
        else:
            print("Erro ao fazer a solicitação à API do YouTube:", error_message)
            return None
      
    return res