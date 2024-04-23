# verification/playlist_verification.py
import json
import datetime

def verificar_e_inserir_log(cur, total_videos_consultados, lista_videos):
    added_videos = []
    removed_videos = []

    #3.1 Antes de gravar o novo log, consulta a lista_videos na tabela blog_consulta_log para identificar inclusão ou exclusão de vídeos da playlist
    cur.execute("SELECT lista_videos FROM blog_consulta_log ORDER BY id DESC LIMIT 1")
    last_log = cur.fetchone()  # Obtém o último registro da tabela blog_consulta_log
    #print("log anterior", last_log)
    
    if last_log:
        last_videos = last_log[0]  # Converte a lista de vídeos do último registro de volta para Python
        added_videos = list(set(lista_videos) - set(last_videos))  # Vídeos adicionados desde o último registro
        removed_videos = list(set(last_videos) - set(lista_videos))  # Vídeos removidos desde o último registro

        if added_videos or removed_videos:
            # Se houver alterações na playlist, execute a inserção do novo log
            print("Vídeos adicionados desde o último registro:", added_videos)
            print("Vídeos removidos desde o último registro:", removed_videos)
            lista_videos_json = json.dumps(lista_videos)
            # Executando o comando INSERT INTO com a lista de vídeos em JSON
            cur.execute("INSERT INTO blog_consulta_log (data, hora, qtd_videos, lista_videos) VALUES (%s, %s, %s, %s)", (datetime.date.today(), datetime.datetime.now().time(), total_videos_consultados, lista_videos_json))
        else:
            # Se não houver registros anteriores, insira o novo log
            print("Nenhum registro consultado anterior encontrado. Inserindo novo log...")
            # Executando o comando INSERT INTO com a lista de vídeos em JSON
            lista_videos_json = json.dumps(lista_videos)
            print(lista_videos_json)
            cur.execute("INSERT INTO blog_consulta_log (data, hora, qtd_videos, lista_videos) VALUES (%s, %s, %s, %s)", (datetime.date.today(), datetime.datetime.now().time(), total_videos_consultados, lista_videos_json))
    else:
        # Se last_log for None, não há registros anteriores, então insira o novo log
        print("Nenhum registro anterior encontrado. Inserindo novo log...")
        # Executando o comando INSERT INTO com a lista de vídeos em JSON
        lista_videos_json = json.dumps(lista_videos)
        #print(lista_videos_json)
        cur.execute("INSERT INTO blog_consulta_log (data, hora, qtd_videos, lista_videos) VALUES (%s, %s, %s, %s)", (datetime.date.today(), datetime.datetime.now().time(), total_videos_consultados, lista_videos_json))

    print("#Log comparado!")
    return added_videos, removed_videos
