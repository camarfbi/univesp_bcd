import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import psycopg2
import sys
sys.path.append("/usr/local/lib/python3.8/dist-packages")
import schedule
import time

# Função para realizar a consulta à API do YouTube e gravar os dados no banco de dados
def consultar_playlist():
    try:
        # Obtenha variáveis de ambiente
        POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
        POSTGRES_DB = os.environ.get('POSTGRES_DB')
        POSTGRES_USER = os.environ.get('POSTGRES_USER')
        POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
        YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
        PLAYLIST_ID = os.environ.get('PLAYLIST_ID')

        # Crie o cliente do YouTube API
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

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

        next_page_token = None
        total_videos_consultados = 0
        videos_ids_bd = []

        # Consultar todos os IDs de vídeos no banco de dados
        cur.execute("SELECT name->>'en_US' FROM blog_post")
        rows = cur.fetchall()
        for row in rows:
            videos_ids_bd.append(row[0])

        while True:
            # Faça a solicitação para obter os itens da playlist com o token da próxima página
            res = youtube.playlistItems().list(
                part='snippet',
                playlistId=PLAYLIST_ID,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            # Processar os resultados desta página
            for item in res['items']:
                title = item['snippet']['title']
                description = item['snippet']['description']
                tags = item['snippet'].get('tags', [])
                video_id = item['snippet']['resourceId']['videoId']  # Obtém o ID do vídeo

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
                    # Insira os dados na tabela blog_post_blog_tag_rel
                    cur.execute("""
                        INSERT INTO blog_post_blog_tag_rel (blog_tag_id, blog_post_id)
                        VALUES (%s, %s)
                    """, (
                        1,  # blog_tag_id (para simplificar, assumindo 1 como ID da playlist)
                        blog_post_id
                    ))

                videos_ids_bd.remove(title)
                total_videos_consultados += 1

            # Atualizar o token da próxima página
            next_page_token = res.get('nextPageToken')

            # Se não houver mais páginas, interrompa o loop
            if not next_page_token:
                break

        # Remover os posts do blog correspondentes aos vídeos removidos da playlist
        if videos_ids_bd:
            for video_title in videos_ids_bd:
                cur.execute("DELETE FROM blog_post WHERE name->>'en_US' = %s", (video_title,))

        # Registre a consulta no log
        cur.execute("INSERT INTO consulta_log (data, hora, videos_consultados) VALUES (%s, %s, %s)", (today, now.time(), total_videos_consultados))

        # Commit e feche a conexão
        conn.commit()
        conn.close()

        print("Consulta realizada com sucesso e dados gravados no banco de dados.")

    except Exception as e:
        # Lidar com falhas na solicitação
        print("Ocorreu um erro ao obter os itens da playlist:", e)

# Agendamento para executar a consulta a cada 6 horas
schedule.every(0.1).hours.do(consultar_playlist)

while True:
    schedule.run_pending()
    time.sleep(1)
