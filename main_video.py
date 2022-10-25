from pathlib import Path

from download_yt import execute_download

if __name__ == "__main__":
    execute_download(destination_folder=Path("/home/daniel.pelati/Videos/"))
