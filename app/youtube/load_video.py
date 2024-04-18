# youtube/load_video.py
def load_video_data(item):
    """
    Carrega os dados do vídeo a partir de um item do YouTube API response.

    Args:
        item (dict): O item do YouTube API response contendo informações sobre o vídeo.

    Returns:
        tuple: Uma tupla contendo o título, descrição, tags, ID do vídeo e URL da miniatura.
    """
    title = item['snippet']['title']
    description = item['snippet']['description']
    tags = item['snippet'].get('tags', [])
    video_id = item['snippet']['resourceId']['videoId']
    # Verificar a disponibilidade da imagem de alta qualidade, se não existir, verificar a média
    if 'high' in item['snippet']['thumbnails']:
        thumbnail_url = item['snippet']['thumbnails']['high']['url']
    elif 'medium' in item['snippet']['thumbnails']:
        thumbnail_url = item['snippet']['thumbnails']['medium']['url']
    else:
        # Caso não haja uma imagem de alta ou média qualidade, escolha outra resolução ou uma imagem padrão
        thumbnail_url = "/web/image/website.s_cover_default_image"
        
    # Imprimir as informações do vídeo
    print(f"Título: {title}, ID do vídeo: {video_id}")
    
    return title, description, tags, video_id, thumbnail_url