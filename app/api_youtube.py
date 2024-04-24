# Version 1.11
# V1.11 - Update posts disable to on


import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import psycopg2

# Importe os módulos necessários
from database.db_connection import create_connection
from youtube.youtube_client import create_youtube_client
from playlist.playlist_items import get_playlist_items
from verification.playlist_verification import verificar_e_inserir_log
from youtube.load_video import load_video_data
from insertion.blog_post_insertion import insert_blog_post
from verification.post_verification import is_post_exist

# Obtenha variáveis de ambiente
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
PLAYLIST_ID = os.environ.get('PLAYLIST_ID')

#1 Crie a conexão com o banco de dados
conn = create_connection()

# Crie um cursor a partir da conexão
cur = conn.cursor()

# Defina a data e hora atual
now = datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')

#2 Crie o cliente do YouTube API
youtube = create_youtube_client()
#print("Cliente do YouTube API criado com sucesso.")  # Mensagem de debug para indicar que o cliente foi criado com sucesso

try:
    next_page_token = None
    total_videos_consultados = 0
    videos_removidos = 0
    videos_adiconados = 0
    lista_videos = []
    status_videos_removed = []
    status_videos_published = []
    added_videos = []
    removed_videos = []
    vr=[]
    va=[]

    while True:
        #3 Faça a solicitação para obter os itens da playlist com o token da próxima página
        res = get_playlist_items(youtube, PLAYLIST_ID, next_page_token)
       
        #print("Lista de vídeos da playlist:") - debug
        #carrega a lista de videos da pleylist
        for item in res['items']:
            video_id = item['snippet']['resourceId']['videoId']  # Obtém o ID do vídeo
            title = item['snippet']['title']
            description = item['snippet']['description']
            tags = item['snippet'].get('tags', [])
            privacy_status = item['status']['privacyStatus']
            # Verificar a disponibilidade da imagem de alta qualidade, se não existir, verificar a média
            if 'high' in item['snippet']['thumbnails']:
                thumbnail_url = item['snippet']['thumbnails']['high']['url']
            elif 'medium' in item['snippet']['thumbnails']:
                thumbnail_url = item['snippet']['thumbnails']['medium']['url']
            else:
                # Caso não haja uma imagem de alta ou média qualidade, escolha outra resolução ou uma imagem padrão
                thumbnail_url = "/web/image/website.s_cover_default_image" 
            
            #Criar um dicionario para cada item
            video_data = {
            'video_id' : video_id,
            'title' : title,
            'description' : description,
            'tags' : tags,
            'privacy_status' : privacy_status,
            'thumbnail_url' : thumbnail_url
            }
            
            if privacy_status == "private" or privacy_status == "unlisted" or privacy_status == "deleted":
                status_videos_removed.append(video_data)
                videos_removidos += 1
            #ignorado video com titulo "private video", "deleted video"
            if title.lower() in ["private video", "deleted video"]:
                status_videos_removed.append(video_data)
                videos_removidos += 1
            else:
                status_videos_published.append(video_data)
                videos_adiconados +=1
            total_videos_consultados += 1
            lista_videos.append(video_id)
            
        if 'nextPageToken' in res:
            next_page_token = res['nextPageToken']
        else:
            # Se não houver mais páginas, saia do loop
            break
            
        
    print("Total de vídeos consultados: ", total_videos_consultados, "Removidos", videos_removidos, "Adicionados",videos_adiconados)

    #######loop para debug#####
    #for video_data in status_videos_removed:
    #    video_id = video_data['video_id']
    #    vr.append(video_id)
    #print("Removidos----------------<b>", vr)
    #for video_data in status_videos_published:
    #    video_id = video_data['video_id']
    #    va.append(video_id)
    #print("Adicionados--------------<b>", va)
    
    #4 Consulta log da playlist
    added_videos, removed_videos = verificar_e_inserir_log(cur, total_videos_consultados, lista_videos)

    # Obter os vídeos removidos da função verificar_e_inserir_log
    removed_videos_arg = removed_videos
    added_videos_arg = added_videos
    print("Vídeos removidos:", removed_videos_arg)
    print("Vídeos removidos:", added_videos_arg)
    
    status_videos_published_jason = json.dumps(status_videos_published)
    status_videos_removed_jason = json.dumps(status_videos_removed)
    
    for video_id in added_videos_arg:
        cur.execute("SELECT b_post_id FROM blog_video_post_relation WHERE b_video_id = %s", (video_id,))
        post_id = cur.fetchone()
        cur.execute("UPDATE blog_post SET active = True WHERE id = %s", (post_id[0],))
        print(f"O post {post_id} associado ao vídeo {video_id} foi ativado.")
    
    
    # 5 Insere ou desativa o post caso haja alteração na playlist
    for video_data in status_videos_published:
        video_id = video_data['video_id']
        insert_blog_post(cur, video_data, today)
        
    # Iterar sobre os vídeos removidos para desativar os posts associados
    for video_id in removed_videos_arg:
        print(f"Desativando o post associado ao vídeo removido: {video_id}")
        cur.execute("SELECT b_post_id FROM blog_video_post_relation WHERE b_video_id = %s", (video_id,))
        post_id = cur.fetchone()
        if post_id:
            # Se encontrar o post correspondente, atualize o campo "active" para False na tabela blog_post
            cur.execute("UPDATE blog_post SET active = False WHERE id = %s", (post_id[0],))
            print(f"O post {post_id} associado ao vídeo {video_id} foi desativado.")
        else:
            # Se não encontrar o post correspondente, imprima uma mensagem indicando que não foi encontrado
            print(f"Não foi possível encontrar o post associado ao vídeo {video_id}.")

    conn.commit()
    conn.close()
    
except Exception as e:
    # Lidar com falhas na solicitação
    print("Ocorreu um erro ao obter os itens da playlist:", e)
