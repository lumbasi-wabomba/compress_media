Media Compression Tool
Compresses images and videos before upload. Two scripts — one for local use via CLI, one for use inside a server pipeline.

Scripts

compress.py — run from the terminal. Prompts you to compress a single image, single video, or an entire folder. Folder output is packaged into a .zip with a compression summary.
compress_prod.py — import into your backend. Pass it a file path, it detects the type, converts images to WebP and videos to H.265, compresses, and saves the result to a processed/ folder.

pythonfrom compress.compress_prod import process_media
output = process_media("/uploads/photo.jpg")

Install

pip install -r requirements.txt

Notes

compress.py uses a bundled ffmpeg — no system install needed.
compress_prod.py calls system ffmpeg — make sure it's on your PATH.
Both scripts delete the original file after processing. Back up first if needed.