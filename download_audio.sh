#!/bin/bash

source ~/dev/small/youtube_download/venv/bin/activate

python3 ~/dev/small/youtube_download/main_audio.py $1

deactivate
