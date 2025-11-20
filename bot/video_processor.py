import os
import subprocess
import uuid
from PIL import Image

async def process_video_with_thumbnail(video_path, thumbnail_path):
    thumb = Image.open(thumbnail_path)
    thumb = thumb.convert('RGB')
    thumb.thumbnail((1280, 720), Image.Resampling.LANCZOS)
    
    temp_thumb = f"downloads/thumb_resized_{uuid.uuid4().hex[:8]}.jpg"
    thumb.save(temp_thumb, 'JPEG', quality=95, optimize=True)
    
    output_path = f"outputs/output_{uuid.uuid4().hex[:8]}.mp4"
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', temp_thumb,
        '-map', '0',
        '-map', '1',
        '-c', 'copy',
        '-c:v:1', 'mjpeg',
        '-disposition:v:1', 'attached_pic',
        '-y',
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Stream copy failed, trying re-encode: {e.stderr}")
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', temp_thumb,
            '-map', '0:v', '-map', '0:a?', '-map', '1',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '18',
            '-c:a', 'copy',
            '-c:v:1', 'mjpeg',
            '-disposition:v:1', 'attached_pic',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    
    if os.path.exists(temp_thumb):
        os.remove(temp_thumb)
    
    return output_path
