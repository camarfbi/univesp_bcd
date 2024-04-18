# insertion/blog_video_post_relation_insertion.py
def insert_blog_video_post_relation(cur, video_id, blog_post_id):
    cur.execute("""
        INSERT INTO blog_video_post_relation (b_video_id, b_post_id)
        VALUES (%s, %s)
    """, (
        video_id,
        blog_post_id
    ))