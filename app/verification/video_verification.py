# verification/video_verification.py
def is_video_valid(cur, title, item, video_id):
    if title.lower() in ["private video", "deleted video"]:
        print(f"IGNORADO: {title}")
        return True

    return False
