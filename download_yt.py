import os
import sys

import yt_dlp as youtube_dl

# import easygui
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from webptools import dwebp
from PIL import Image

ONLY_AUDIO = True
# ONLY_AUDIO = False
#
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


class MyLogger(object):
    def debug(self, msg):
        print(msg)
        if "[ffmpeg] Destination: " in msg:
            paths_audio.append(Path(msg.replace("[ffmpeg] Destination: ", "")))
        elif "[download] Destination: " in msg:
            paths_video.append(Path(msg.replace("[download] Destination: ", "")))
        elif "Writing thumbnail to: " in msg:
            paths_images.append(Path(msg.split("Writing thumbnail to: ")[-1]))

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


ydl_opts_video = {
    # 'format': 'bestaudio/best',  # choice of quality
    # 'format': '140/134',  # choice of quality ; see formats above
    # 'extractaudio': True,  # only keep the audio
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
        {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192",}
    ],
    # 'postprocessors': [{
    #     'key': 'FFmpegVideoConvertor',
    #     'preferedformat': 'avi',
    # }],
    "ignoreerrors": True,
    "forcefilename": True,
    "logger": MyLogger(),
    "keepvideo" : True
}


def download_from_youtube(video_url, destination_folder, ydl_opts):
    if "playlist" in video_url or "list" in video_url:
        path = destination_folder / "%(playlist)s" / "%(playlist_index)s _ %(title)s.%(ext)s"
    else:
        path = destination_folder / "%(title)s.%(ext)s"

    ydl_opts["outtmpl"] = str(path)

    ydl = youtube_dl.YoutubeDL(ydl_opts)

    with ydl:
        result = ydl.extract_info(video_url, download=True)

    if "entries" in result:
        result_titles = []
        # Can be a playlist or a list of videos
        for video in result["entries"]:
            print(video["webpage_url"])
            print(video["title"])
            result_titles.append(video["title"])
        return result_titles
    else:
        # Just a video
        print(result["webpage_url"])
        print(result["title"])
        # print(video["format"])
    return [result["title"]]


def add_cover_mp3(audio_path, image_file):
    picture_path = image_file.with_suffix(".jpg")

    if image_file.suffix == ".webp":
        im = Image.open(image_file).convert("RGB")
        im.save(picture_path)
        image_file.unlink()

    if picture_path.exists():
        audio = MP3(audio_path, ID3=ID3)
        # adding ID3 tag if it is not present
        try:
            audio.add_tags()
        except:
            pass
        audio.tags.add(
            APIC(mime="image/jpeg", type=3, desc="Cover", data=open(picture_path, "rb").read(),)
        )
        # edit ID3 tags to open and read the picture from the path specified and assign it
        audio.save()  # save the current changes
        picture_path.unlink()
    else:
        raise Exception(f"picture not found {picture_path}")


def execute_main():
    global paths_video, paths_audio, paths_images
    paths_video = []
    paths_audio = []
    paths_images = []
    video_urls = []
    if len(sys.argv) == 1:
        print("Donne moi l'adresse youtube")
        while True:
            video_urls = [input(">")]
            if "youtube.com/" in video_urls[0] or 'youtu.be' in video_urls[0]:
                break
            else:
                print("Ceci n'est pas une adresse youtube, reessayer")
                continue
    else:
        video_urls = sys.argv[1:]
    # destination_folder = easygui.diropenbox()
    for video_url in video_urls:
        if ONLY_AUDIO:
            destination_folder = Path("/home/daniel.pelati/Music/")
            print("Destination folder: ", destination_folder)
            titles = download_from_youtube(video_url, destination_folder, ydl_opts_audio)

            for count, audio in enumerate(paths_audio):
                add_cover_mp3(audio, paths_images[count])
        else:
            destination_folder = Path("/home/daniel.pelati/Videos/")
            print("Destination folder: ", destination_folder)
            download_from_youtube(video_url, destination_folder, ydl_opts_video)


if __name__ == "__main__":
    execute_main()
