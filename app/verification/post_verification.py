# verification/post_verification.py
def is_post_exist(cur, video_id):
    cur.execute("SELECT b_video_id FROM blog_video_post_relation WHERE b_video_id = %s", (video_id,))
    existing_video = cur.fetchone()
    if existing_video:
        return True
    return False