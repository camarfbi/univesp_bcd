# Version 1.02
# Ckeck and ignore videos private or deleted.
# Converted form procedural to object-oriented mode


import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import psycopg2

# Importe os módulos necessários
from database.db_connection import create_connection #1
from youtube.youtube_client import create_youtube_client #2
from playlist.playlist_items import get_playlist_items #3
from youtube.load_video import load_video_data #4
from verification.video_verification import is_video_valid #5
from verification.post_verification import is_post_exist #6
from insertion.blog_post_insertion import insert_blog_post #7
from insertion.blog_post_blog_tag_rel_insertion import insert_blog_post_blog_tag_rel #8
from insertion.blog_video_post_relation_insertion import insert_blog_video_post_relation #9
from insertion.blog_consulta_lo import insert_bl_consulta_log #10


# Defina a data e hora atual
now = datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')

#1 Obtenha variáveis de ambiente
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
PLAYLIST_ID = os.environ.get('PLAYLIST_ID')

# Crie a conexão com o banco de dados
conn = create_connection()

# Crie um cursor a partir da conexão
cur = conn.cursor()

#2 Crie o cliente do YouTube API
youtube = create_youtube_client()
print("Cliente do YouTube API criado com sucesso.")  # Mensagem de debug para indicar que o cliente foi criado com sucesso

try:
    next_page_token = None
    total_videos_consultados = 0
    videos_consultados_pagina = 0
    lista_videos = []

    while True:
        #3 Faça a solicitação para obter os itens da playlist com o token da próxima página
        res = get_playlist_items(youtube, PLAYLIST_ID, next_page_token)
        
        # Verificar se a resposta indica um erro de limite de consulta
        if 'error' in res:
            error_message = res['error']['message']
            if 'quota' in error_message.lower():
                print("Limite de consulta à API do YouTube excedido. Aguarde antes de tentar novamente.")
                break
            else:
                print("Erro ao fazer a solicitação à API do YouTube:", error_message)
                break
       
        # Processar os resultados desta página
        for item in res['items']:
            
            #4 Chamada à função load_video_data sem passar argumentos extras
            title, description, tags, video_id, thumbnail_url = load_video_data(item)
            
            #5 Verificar se o vídeo é privado ou foi excluído
            if is_video_valid(cur, title, item, video_id):
                continue
                
            #6 Verificar se o video já foi postado
            
            existing_video = is_post_exist(cur, video_id)
            if existing_video:
                print("Já foi postado")
                continue

        #7 Insira os dados na tabela blog_post
        insert_blog_post(cur, title, description, video_id, thumbnail_url, today)

        # Recupere o ID do blog_post inserido
        cur.execute("SELECT currval(pg_get_serial_sequence('blog_post', 'id'))")
        blog_post_id = cur.fetchone()[0]

        #8 Insira os dados na tabela blog_post_blog_tag_rel
        insert_blog_post_blog_tag_rel(cur, blog_post_id)

        #9 Insira o video_id na tabela blog_video_post_relation
        insert_blog_video_post_relation(cur, video_id, blog_post_id)

        videos_consultados_pagina += 1
        total_videos_consultados += 1
        lista_videos.append(video_id)

        # Atualizar o token da próxima página
        next_page_token = res.get('nextPageToken')

        # Se não houver mais páginas, interrompa o loop
        if not next_page_token:
            break
    
 
    # Convertendo a lista para JSON
    lista_videos_json = json.dumps(lista_videos)

    # Executando o comando INSERT INTO com a lista de vídeos em JSON
    #cur.execute("INSERT INTO blog_consulta_log (data, hora, qtd_videos, lista_videos) VALUES (%s, %s, %s, %s)", (today, now.time(), total_videos_consultados, lista_videos_json))
    insert_bl_consulta_log(cur, today, now, total_videos_consultados, lista_videos)
    
    # Commit e feche a conexão
    conn.commit()
    conn.close()

except Exception as e:
    # Lidar com falhas na solicitação
    print("Ocorreu um erro ao obter os itens da playlist:", e)