# insertion/insert_blog_post.py
import json
from insertion.blog_video_post_relation_insertion import insert_blog_video_post_relation
from insertion.blog_post_blog_tag_rel_insertion import insert_blog_post_blog_tag_rel
from verification.post_verification import is_post_exist

def insert_blog_post(cur, video_data, today):
    video_id = video_data['video_id']
    title = video_data['title']
    description = video_data['description']
    tags = video_data['tags']
    thumbnail_url = video_data['thumbnail_url']
    existing_video = is_post_exist(cur, video_id)
    if existing_video:
        #print(f"O vídeo {video_id} já foi postado.")
        return

    # Aqui você pode continuar com o resto do seu código, utilizando as variáveis video_id, title, description, tags, etc.
    # Certifique-se de fazer as substituições necessárias em todo o código para usar essas variáveis.

    name_json = json.dumps({"en_US": title, "pt_BR": title})
    content_json = json.dumps({
        "en_US": f'<iframe width="720" height="405" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe><p class="o_default_snippet_text">{description}</p>',
        "pt_BR": f'<iframe width="720" height="405" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe><p class="o_default_snippet_text">{description}</p>'
    })

    cover_properties_json = json.dumps({
        "background-image": f"url({thumbnail_url})",
        "background_color_class": "o_cc3 o_cc",
        "background_color_style": "",
        "opacity": "0.2",
        "resize_class": "o_half_screen_height o_record_has_cover",
    })
    
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

    cur.execute("SELECT currval(pg_get_serial_sequence('blog_post', 'id'))")
    blog_post_id = cur.fetchone()[0]
    #print(f"Vídeos adicionados: {blog_post_id} - {video_id}")
    insert_blog_post_blog_tag_rel(cur, blog_post_id)
    insert_blog_video_post_relation(cur, video_id, blog_post_id)
