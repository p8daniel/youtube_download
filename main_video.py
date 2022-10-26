from pathlib import Path


from download_yt import execute_download


def get_video_destination_directory() -> Path:
    music_path_folders = [
        Path.home() / "Video",
        Path("%HOMEPATH%/Video"),
        Path("%UserProfile%/Video"),
    ]
    for path in music_path_folders:
        if path.exists():
            return path
    import easygui as easygui

    return Path(easygui.diropenbox())


def main():
    destination_folder = get_video_destination_directory()
    execute_download(only_audio=False, destination_folder=destination_folder)


if __name__ == "__main__":
    main()
