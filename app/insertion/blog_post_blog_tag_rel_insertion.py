# insertion/blog_post_blog_tag_rel_insertion.py
def insert_blog_post_blog_tag_rel(cur, blog_post_id):
    cur.execute("""
        INSERT INTO blog_post_blog_tag_rel (blog_tag_id, blog_post_id)
        VALUES (%s, %s)
    """, (
        1,  # blog_tag_id
        blog_post_id
    ))
