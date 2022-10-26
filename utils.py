from enum import Enum
from pathlib import Path


class DefaultFolderType(str, Enum):
    VIDEO = "Videos"
    MUSIC = "Music"


def get_console_confirmation(request_message: str) -> bool:
    """Get confirmation from the user"""
    while True:
        answer = input(request_message + " [Y/n] (default: y) ")
        if answer.lower() in ["", "y", "yes"]:
            return True
        elif answer.lower() in ["n", "no"]:
            return False
        else:
            print("Je n'ai pas compris")


def get_destination_directory(default_folder: DefaultFolderType) -> Path:
    default_folder_path = Path.home() / default_folder.value
    if default_folder_path.exists():
        confirmation_msg = (
            f"Le fichier sera téléchargé dans: '{default_folder_path}' "
            "Continuer avec cet emplacement?"
        )
        if get_console_confirmation(request_message=confirmation_msg):
            return default_folder_path
    import easygui as easygui

    return Path(easygui.diropenbox(title="Dossier de destination"))
