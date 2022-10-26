import logging
import os
import re
import sys
from typing import Dict

import yt_dlp as youtube_dl


from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

logger = logging.getLogger("mylogger")
logger.setLevel(logging.DEBUG)

# https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312  for options
# https://github.com/ytdl-org/youtube-dl/blob/master/README.md#readme
# https://github.com/ytdl-org/youtube-dl/blob/master/README.md#format-selection

# format code extension resolution  note
# 140         m4a       audio only  DASH audio , audio@128k (worst)
# 160         mp4       144p        DASH video , video only
# 133         mp4       240p        DASH video , video only
# 134         mp4       360p        DASH video , video only
# 135         mp4       480p        DASH video , video only
# 136         mp4       720p        DASH video , video only
# 17          3gp       176x144
# 36          3gp       320x240
# 5           flv       400x240
# 43          webm      640x360
# 18          mp4       640x360
# 22          mp4       1280x720    (best)

DEFAULT_FOLDER = Path(__file__).parent / "download"

paths_video = []
paths_audio = []
paths_images = []
webp_pattern = re.compile(
    r"\[info\] Writing video thumbnail ([0-9]+ )?to: (?P<path>.*\.(webp|jpg|png))"
)


class MyLogger(object):
    def debug(self, msg):
        logger.info(msg)
        global paths_video, paths_audio, paths_images
        if "[ExtractAudio] Destination: " in msg:
            paths_audio.append(Path(msg.replace("[ExtractAudio] Destination: ", "")))
        elif "[download] Destination: " in msg:
            paths_video.append(Path(msg.replace("[download] Destination: ", "")))
        elif "Writing thumbnail to: " in msg:
            paths_images.append(Path(msg.split("Writing thumbnail to: ")[-1]))
        elif match := re.match(webp_pattern, msg):
            paths_images.append(Path(match.group("path")))

    def warning(self, msg):
        logger.warning(msg)

    def error(self, msg):
        logger.error(msg)


ydl_opts_video = {
    # 'format': 'bestaudio/best',  # choice of quality
    # 'format': '140/134',  # choice of quality ; see formats above
    # "ignoreerrors": True
}

ydl_opts_audio = {
    "writethumbnail": True,
    # 'format': 'bestaudio/best',  # choice of quality
    "format": "140/134",  # choice of quality ; see formats above
    # 'extractaudio': True,  # only keep the audio
    # 'audioformat': "mp3",  # convert to mp3
    # 'outtmpl': '%(id)s',  # name the file the ID of the video
    # 'noplaylist': True,  # only download single song, not playlist
    #
    "postprocessors": [
        {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
    ],
    "ignoreerrors": True,
    "forcefilename": True,
    "logger": MyLogger(),
    "keepvideo": False,
}


def download_from_youtube(video_url, destination_folder, ydl_options: Dict):
    if "playlist" in video_url or "list" in video_url:
        path = destination_folder / "%(playlist)s" / "%(playlist_index)s _ %(title)s.%(ext)s"
    else:
        path = destination_folder / "%(title)s.%(ext)s"

    ydl_options["outtmpl"] = str(path)

    ydl = youtube_dl.YoutubeDL(ydl_options)

    with ydl:
        result = ydl.extract_info(video_url, download=True)

    if "entries" in result:
        result_titles = []
        # Can be a playlist or a list of videos
        for video in result["entries"]:
            logger.info(video["webpage_url"])
            logger.info(video["title"])
            result_titles.append(video["title"])
        return result_titles
    else:
        # Just a video
        logger.info(result["webpage_url"])
        logger.info(result["title"])
    return [result["title"]]


def add_cover_mp3(image_path: Path):
    audio_path = image_path.parent / f"{image_path.stem}.mp3"
    if not audio_path.exists():
        logger.error(f"The audio file {audio_path} does not exists and the cover cannot be added")
        return
    converted_image_path = image_path.parent / f"{image_path.stem}.jpg"

    if image_path.suffix == ".webp" or image_path.suffix == ".png":
        logger.info(f"Converting {image_path} to jpg")
        im = Image.open(image_path).convert("RGB")
        im.save(converted_image_path, "jpeg")
        logger.info(f"Deleting {image_path} to jpg")
        image_path.unlink()  # delete the file

    if not converted_image_path.exists():
        logger.error(f"Picture {converted_image_path} not found")
        return

    audio = MP3(audio_path, ID3=ID3)
    # adding ID3 tag if it is not present
    try:
        audio.add_tags()
    except:
        pass
    audio.tags.add(
        APIC(mime="image/jpeg", type=3, desc="Cover", data=open(converted_image_path, "rb").read())
    )
    # edit ID3 tags to open and read the picture from the path specified and assign it
    audio.save()  # save the current changes
    logger.info(f"Deleting {converted_image_path} to jpg")
    converted_image_path.unlink()


def execute_download(only_audio: bool = False, destination_folder: Path = DEFAULT_FOLDER):

    global paths_video, paths_audio, paths_images
    if len(sys.argv) == 1:
        print("Donne moi l'adresse youtube")
        while True:
            video_urls = [input(">")]
            if "youtube.com/" in video_urls[0] or "youtu.be" in video_urls[0]:
                break
            else:
                print("Ceci n'est pas une adresse youtube, reessayer")
                continue
    else:
        video_urls = sys.argv[1:]
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    logger.info("Destination folder: ", destination_folder)
    for video_url in video_urls:
        if only_audio:
            try:
                titles = download_from_youtube(
                    video_url, destination_folder, ydl_options=ydl_opts_audio
                )
            except (Exception, KeyboardInterrupt) as exc:
                logger.exception(exc)
            for count, image in enumerate(paths_images):
                add_cover_mp3(image)
        else:
            download_from_youtube(video_url, destination_folder, ydl_opts_video)
