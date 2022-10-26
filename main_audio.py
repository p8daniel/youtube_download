from pathlib import Path


from download_yt import execute_download


def main():
    destination_folder = get_music_destination_directory()
    execute_download(only_audio=True, destination_folder=destination_folder)


def get_music_destination_directory() -> Path:
    music_path_folders = [
        Path.home() / "Music",
        # Path("%HOMEPATH%/Music"),
        # Path("%UserProfile%/Music"),
    ]
    for path in music_path_folders:
        if path.exists():
            return path
    import easygui as easygui

    return Path(easygui.diropenbox())


if __name__ == "__main__":
    main()
