# media compression module
# images: uses PIL to compress images by reducing quality and resizing
# once image uploaded its put in a temp folder, format detected, converted to webp, compressed and optimised
# video compression function : uses ffmpeg to compress videos by reducing bitrate and resolution
# once video uploaded its put in a temp folder, format detected, converted to HEVC (h265) format, compressed and optimised

import imageio_ffmpeg as iio_ffmpeg
import os
import subprocess
from PIL import Image, ImageFilter
from pathlib import Path

INPUT_FOLDER = "uploads"
OUTPUT_FOLDER = "processed"

Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
video_extensions = ['.mp4', '.mkv', '.avi', '.mov']


# image format detection & conversion:
def img_conv_format(image_path):
    img = Image.open(image_path)
    if img.format != 'WEBP':
        webp_path = os.path.splitext(image_path)[0] + '.webp'
        img = img.convert("RGB")
        img.save(webp_path,'WEBP',quality=82,method=6)
    
        os.remove(image_path)
        return webp_path
    return image_path

# video format detection & conversion:
def vid_conv_format(video_path):
    video_ext = os.path.splitext(video_path)[1].lower()

    if video_ext not in video_extensions:
        raise ValueError("Unsupported video format")
    hevc_path = os.path.splitext(video_path)[0] + '_hevc.mp4'

    command = [
        'ffmpeg',
        '-i', video_path,
        '-c:v', 'libx265',
        '-c:a', 'aac',
        '-b:a', '128k',
        hevc_path
    ]

    subprocess.run(command, check=True)
    os.remove(video_path)
    return hevc_path

# image compression:
def compress_image(img_path, quality=80, method=6, size=(1600,1600)):
    img = Image.open(img_path)
    img = img.convert('RGB')
    img.thumbnail(size, Image.ANTIALIAS)
    img = img.filter(ImageFilter.SHARPEN)

    output_file = Path(OUTPUT_FOLDER) / f"{Path(img_path).stem}.webp"
    img.save(output_file, 'WEBP', quality=quality, method=method)
    os.remove(img_path)
    return output_file

# video compression:
def compress_video(video_path):
    video_path = Path(video_path)
    output_folder = Path(OUTPUT_FOLDER)
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / f"{video_path.stem}_compressed.mp4"

    command = [
        'ffmpeg',
        '-i', str(video_path),
        '-c:v', 'libx265',
        '-crf', '28',
        '-preset', 'slow',
        '-c:a', 'aac',
        '-b:a', '128k',
        str(output_file)
    ]

    try:
        subprocess.run(command, check=True)
        os.remove(video_path)
        return output_file
    except subprocess.CalledProcessError as e:
        print("Compression failed:", e)
        return None

# utility function to normalize file paths
def normalize_path(path_input):
    return os.path.abspath(os.path.expanduser(path_input.strip()))

# entry function
def process_media(file_path):
    file_path = normalize_path(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    if ext in image_extensions:
        converted_path = img_conv_format(file_path)
        return compress_image(converted_path)
    elif ext in video_extensions:
        converted_path = vid_conv_format(file_path)
        return compress_video(converted_path)
    else:
        raise ValueError("Unsupported file type")

