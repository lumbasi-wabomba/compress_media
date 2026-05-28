import imageio_ffmpeg as iio_ffmpeg
import os
import subprocess
from PIL import Image
import zipfile
import shutil
from pathlib import Path

# Get ffmpeg executable path inside the virtual environment
ffmpeg_path = iio_ffmpeg.get_ffmpeg_exe()
print("FFmpeg path:", ffmpeg_path)

def normalize_path(path_input):
    """
    Expands ~, removes extra spaces, and converts to absolute path.
    """
    return os.path.abspath(os.path.expanduser(path_input.strip()))

def compress_video(input_path, crf=30):
    try:
        if not os.path.isfile(input_path):
            print(f"Input file {input_path} does not exist.")
            return None

        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

        cmd = [
            ffmpeg_path,
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", str(crf),
            "-preset", "slow",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-acodec", "aac",
            "-b:a", "128k",
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Video compressed successfully: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def compress_image(input_path, compression_ratio=0.35):
    try:
        if not os.path.isfile(input_path):
            print(f"Input file {input_path} does not exist.")
            return None

        img = Image.open(input_path)
        scale_factor = 1 - compression_ratio
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)

        compressed_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

        compressed_img.save(output_path, quality=85, optimize=True)
        print(f"Image compressed successfully: {output_path}")

        return output_path

    except Exception as e:
        print(f"An error occurred while compressing image: {e}")
        return None

def is_image_file(file_path):
    """Check if file is an image based on extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.ico'}
    return Path(file_path).suffix.lower() in image_extensions

def is_video_file(file_path):
    """Check if file is a video based on extension."""
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.3gp', '.ogv'}
    return Path(file_path).suffix.lower() in video_extensions

def compress_folder(folder_path, target_compression=0.40):
    """
    Compress all videos and images in a folder and save as zip with 40% overall compression target.

    Args:
        folder_path (str): Path to the folder containing media files
        target_compression (float): Target compression ratio (default: 0.40 for 40%)
    """
    try:
        if not os.path.isdir(folder_path):
            print(f"Folder {folder_path} does not exist.")
            return

        temp_dir = os.path.join(folder_path, "_compressed_temp")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        total_original_size = 0
        total_compressed_size = 0
        compressed_files = []

        print(f"\nProcessing folder: {folder_path}")
        print("=" * 60)

        for root, dirs, files in os.walk(folder_path):
            if "_compressed_temp" in root:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                original_size = os.path.getsize(file_path)
                total_original_size += original_size

                compressed_path = None

                if is_image_file(file_path):
                    print(f"\nCompressing image: {file}")
                    compressed_path = compress_image(file_path, compression_ratio=0.35)

                elif is_video_file(file_path):
                    print(f"\nCompressing video: {file}")
                    compressed_path = compress_video(file_path, crf=35)

                if compressed_path and os.path.exists(compressed_path):
                    temp_file_path = os.path.join(temp_dir, os.path.basename(compressed_path))
                    shutil.move(compressed_path, temp_file_path)
                    compressed_size = os.path.getsize(temp_file_path)
                    total_compressed_size += compressed_size
                    compressed_files.append(temp_file_path)

        if compressed_files:
            base_folder_name = os.path.basename(folder_path.rstrip(os.sep))
            zip_path = os.path.join(folder_path, f"{base_folder_name}_compressed.zip")

            print("\n" + "=" * 60)
            print(f"Creating zip file: {zip_path}")

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in compressed_files:
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)

            zip_size = os.path.getsize(zip_path)
            overall_compression = ((total_original_size - zip_size) / total_original_size) * 100

            print("\n" + "=" * 60)
            print("COMPRESSION SUMMARY")
            print("=" * 60)
            print(f"Original total size: {total_original_size:,} bytes ({total_original_size / (1024*1024):.2f} MB)")
            print(f"Zip file size: {zip_size:,} bytes ({zip_size / (1024*1024):.2f} MB)")
            print(f"Overall compression achieved: {overall_compression:.2f}%")
            print(f"Target compression: {target_compression * 100:.0f}%")
            print(f"Status: {'✓ Target achieved' if overall_compression >= target_compression * 100 else '✗ Target not met'}")
            print("=" * 60)

            shutil.rmtree(temp_dir)
            print(f"\nCompressed folder saved to: {zip_path}")
        else:
            print("No media files found to compress.")
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"An error occurred while compressing folder: {e}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    print("Media Compression Tool")
    print("=" * 60)
    print("1. Compress single video")
    print("2. Compress single image")
    print("3. Compress entire folder (mixed videos/images)")
    print("=" * 60)

    choice = input("Select option (1-3): ").strip()

    if choice == "1":
        input_video = normalize_path(input("Enter the path to the input video: "))
        compress_video(input_video)
    elif choice == "2":
        input_image = normalize_path(input("Enter the path to the input image: "))
        compress_image(input_image)
    elif choice == "3":
        input_folder = normalize_path(input("Enter the path to the folder: "))
        compress_folder(input_folder, target_compression=0.35)

if __name__ == "__main__":
    main()
