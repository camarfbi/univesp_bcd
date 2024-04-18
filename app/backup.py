# Version 1.02
# converting code snippets into functions


import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import psycopg2

# Importe os módulos necessários
from database.db_connection import create_connection # 1
from youtube.youtube_client import create_youtube_client#2
from playlist.playlist_items import get_playlist_items #3
from youtube.load_video import load_video_data #4
from verification.video_verification import is_video_valid #5
from verification.post_verification import is_post_exist
from insertion.blog_post_insertion import insert_blog_post
from insertion.blog_post_blog_tag_rel_insertion import insert_blog_post_blog_tag_rel
from insertion.blog_video_post_relation_insertion import insert_blog_video_post_relation
from insertion.blog_consulta_lo import insert_bl_consulta_log

# Obtenha variáveis de ambiente
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

# Defina a data e hora atual
now = datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')



try:
    next_page_token = None
    total_videos_consultados = 0
    lista_videos = []

    while True:
        # Faça a solicitação para obter os itens da playlist com o token da próxima página
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
        if 'items' in res:
            for item in res['items']:
                #4 Chamada à função load_video_data sem passar argumentos extras
                title, description, tags, video_id, thumbnail_url = load_video_data(item)
                print("Título: ", title, "ID do vídeo:", video_id)  # Mensagem de debug para exibir o ID do vídeo

                # Verificar se o vídeo é privado ou foi excluído
                if is_video_valid(cur, title, item, video_id):
                    continue
                # Verificar se o video já foi postado
                existing_video = is_post_exist(cur, video_id)
                if existing_video:
                    print("Já foi postado")
                    continue
        else:
            print("A lista de itens está vazia ou não está presente na resposta.")

            # Inserir o post de novo vídeo
            videos_consultados_pagina = 0
            if not existing_video:
                # Insira os dados na tabela blog_post
                insert_blog_post(cur, title, description, video_id, thumbnail_url, today)

                # Recupere o ID do blog_post inserido
                cur.execute("SELECT currval(pg_get_serial_sequence('blog_post', 'id'))")
                blog_post_id = cur.fetchone()[0]

                # Insira os dados na tabela blog_post_blog_tag_rel
                insert_blog_post_blog_tag_rel(cur, blog_post_id)

                # Insira o video_id na tabela blog_video_post_relation
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
    insert_bl_consulta_log(cur, today, now, total_videos_consultados, lista_videos)

    # Commit e feche a conexão
    conn.commit()
    conn.close()