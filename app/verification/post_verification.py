# verification/post_verification.py
def get_posted_videos(cur):
    cur.execute("SELECT b_video_id FROM blog_video_post_relation")
    posted_videos = cur.fetchall()
    return [video[0] for video in posted_videos]

# Função is_post_exist para chamar a função get_posted_videos
def is_post_exist(cur, video_id):
    cur.execute("SELECT b_post_id FROM blog_video_post_relation WHERE b_video_id = %s", (video_id,))
    existing_video = cur.fetchone()
    if existing_video:
        blog_post_id = existing_video[0]
        return blog_post_id
    return None