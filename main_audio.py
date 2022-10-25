from pathlib import Path

from download_yt import execute_download

if __name__ == "__main__":
    execute_download(only_audio=True, destination_folder=Path("/home/daniel.pelati/Music/"))
