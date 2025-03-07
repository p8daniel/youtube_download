#!/bin/bash


source ~/dev/github_p8daniel/youtube_download/.venv/bin/activate

python3 ~/dev/github_p8daniel/youtube_download/main_audio.py $@

deactivate
