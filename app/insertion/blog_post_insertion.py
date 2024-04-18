# insertion/blog_post_insertion.py
import json
from datetime import datetime

def insert_blog_post(cur, title, description, video_id, thumbnail_url, today):
    # Verificar a disponibilidade da imagem de alta qualidade, se não existir, verificar a média
    if 'high' in item['snippet']['thumbnails']:
        thumbnail_url = item['snippet']['thumbnails']['high']['url']
    elif 'medium' in item['snippet']['thumbnails']:
        thumbnail_url = item['snippet']['thumbnails']['medium']['url']
    else:
        # Caso não haja uma imagem de alta ou média qualidade, escolha outra resolução ou uma imagem padrão
        thumbnail_url = "/web/image/website.s_cover_default_image"    

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
        1,  # blog_id
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