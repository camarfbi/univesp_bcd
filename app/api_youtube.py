# Version 1.01
# Ckeck and ignore videos private or deleted.


import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import psycopg2

# Obtenha variáveis de ambiente
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
PLAYLIST_ID = os.environ.get('PLAYLIST_ID')

# Crie o cliente do YouTube API
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
print("Cliente do YouTube API criado com sucesso.")  # Mensagem de debug para indicar que o cliente foi criado com sucesso

# Defina a conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    host=POSTGRES_HOST,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)
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
        res = youtube.playlistItems().list(
            part='snippet',
            playlistId=PLAYLIST_ID,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        # Verificar se a resposta indica um erro de limite de consulta
        if 'error' in res:
            error_message = res['error']['message']
            if 'quota' in error_message.lower():
                print("Limite de consulta à API do YouTube excedido. Aguarde antes de tentar novamente.")
                break
            else:
                print("Erro ao fazer a solicitação à API do YouTube:", error_message)
                break

        # Debug: Imprimir a lista de vídeos da playlist
        print("Lista de vídeos da playlist:")
        for item in res['items']:
            print(item['snippet']['title'])

        # Inicialize a contagem de vídeos consultados nesta página
        videos_consultados_pagina = 0

        # Processar os resultados desta página
        for item in res['items']:
            title = item['snippet']['title']
            
            # Verificar se o vídeo é privado ou foi excluído
            if title.lower() in ["private video", "deleted video"]:
                print(f"Ignorando vídeo com título: {title}")
                continue

            print("Título do vídeo:", title)  # Mensagem de debug para exibir o título do vídeo
            description = item['snippet']['description']
            tags = item['snippet'].get('tags', [])
            video_id = item['snippet']['resourceId']['videoId']  # Obtém o ID do vídeo
            print("ID do vídeo:", video_id)  # Mensagem de debug para exibir o ID do vídeo

            # Verificar a disponibilidade da imagem de alta qualidade, se não existir, verificar a média
            if 'high' in item['snippet']['thumbnails']:
                thumbnail_url = item['snippet']['thumbnails']['high']['url']
            elif 'medium' in item['snippet']['thumbnails']:
                thumbnail_url = item['snippet']['thumbnails']['medium']['url']
            else:
                # Caso não haja uma imagem de alta ou média qualidade, escolha outra resolução ou uma imagem padrão
                thumbnail_url = "/web/image/website.s_cover_default_image"

            # Verifique se o vídeo já existe na tabela
            cur.execute("SELECT id FROM blog_post WHERE name->>'en_US' = %s", (title,))
            existing_video = cur.fetchone()

            if not existing_video:
                # Insira os dados na tabela blog_post
                name_json = json.dumps({"en_US": title, "pt_BR": title})
                content_json = json.dumps({
                    "en_US": f'<iframe width="720" height="405" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe><p class="o_default_snippet_text">{description}</p>',
                    "pt_BR": f'<iframe width="720" height="405" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe><p class="o_default_snippet_text">{description}</p>'
                })
                cover_properties_json = json.dumps({"background-image": f"url({thumbnail_url})", "background_color_class": "o_cc3 o_cc", "background_color_style": "", "opacity": "0.2", "resize_class": "o_half_scr>"})

                cur.execute("""
                    INSERT INTO blog_post (website_id, author_id, blog_id, create_uid, write_uid, visits, website_meta_og_img,
                    author_name, name, content, cover_properties, is_published, active, create_date, published_date, post_date, write_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    1,  # website_id
                    3,  # author_id
                    1,  # blog_id (para simplificar, assumindo 1 como ID da playlist)
                    2,  # create_uid
                    2,  # write_uid
                    0,  # visits
                    None,  # website_meta_og_img
                    "Escola do Legislativo",  # author_name
                    name_json,  # name
                    content_json,  # content
                    cover_properties_json,  # cover_properties
                    True,  # is_published
                    True,  # active
                    today,  # create_date
                    today,  # published_date
                    today,  # post_date
                    today   # write_date
                ))

                # Recupere o ID do blog_post inserido
                cur.execute("SELECT currval(pg_get_serial_sequence('blog_post', 'id'))")
                blog_post_id = cur.fetchone()[0]
                # print("ID do post inserido:", blog_post_id)  # Mensagem de debug para exibir o ID do post inserido

                # Insira os dados na tabela blog_post_blog_tag_rel
                cur.execute("""
                    INSERT INTO blog_post_blog_tag_rel (blog_tag_id, blog_post_id)
                    VALUES (%s, %s)
                """, (
                    1,  # blog_tag_id (para simplificar, assumindo 1 como ID da playlist)
                    blog_post_id
                ))

                # Insira o video_id na tabela blog_video_post_relation
                cur.execute("""
                    INSERT INTO blog_video_post_relation (b_video_id, b_post_id)
                    VALUES (%s, %s)
                """, (
                    video_id,
                    blog_post_id
                ))

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
        cur.execute("INSERT INTO blog_consulta_log (data, hora, qtd_videos, lista_videos) VALUES (%s, %s, %s, %s)", (today, now.time(), total_videos_consultados, lista_videos_json))
        
    # Commit e feche a conexão
    conn.commit()
    conn.close()

except Exception as e:
    # Lidar com falhas na solicitação
    print("Ocorreu um erro ao obter os itens da playlist:", e)