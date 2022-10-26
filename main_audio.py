from download_yt import execute_downloads
from utils import DefaultFolderType, get_destination_directory


def main():
    destination_folder = get_destination_directory(default_folder=DefaultFolderType.MUSIC)
    execute_downloads(only_audio=True, destination_folder=destination_folder)


if __name__ == "__main__":
    main()
