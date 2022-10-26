from enum import Enum
from pathlib import Path


class DefaultFolderType(str, Enum):
    VIDEO = "Videos"
    MUSIC = "Music"


def get_destination_directory(default_folder: DefaultFolderType) -> Path:
    music_path_folders = [
        Path.home() / default_folder.value,
        # Path("%HOMEPATH%/Videos"),
        # Path("%UserProfile%/Videos"),
    ]
    for path in music_path_folders:
        if path.exists():
            return path
    import easygui as easygui

    return Path(easygui.diropenbox())
