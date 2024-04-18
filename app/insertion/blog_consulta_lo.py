# insertion/blog_consulta_log_insertion.py
import json

# Definindo a função de inserção de log
def insert_bl_consulta_log(cur, today, now, total_videos_consultados, lista_videos):
    lista_videos_json = json.dumps(lista_videos)

    # Executando o comando INSERT INTO com a lista de vídeos em JSON
    cur.execute("""
    INSERT INTO blog_consulta_log (data, hora, qtd_videos, lista_videos) VALUES (%s, %s, %s, %s)
    """, (
        today, now.time(),
        total_videos_consultados,
        lista_videos_json
    ))