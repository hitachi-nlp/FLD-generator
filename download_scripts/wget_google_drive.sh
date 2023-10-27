#!/bin/bash

GOOGLE_DRIVE_ID="${1}"
OUTPUT_FILENAME="${2}"

CONFIRM=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate "https://drive.google.com/uc?export=download&id=$GOOGLE_DRIVE_ID" -O- | sed -En 's/.*confirm=([0-9A-Za-z_]+).*/\1/p');
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$CONFIRM&id=$GOOGLE_DRIVE_ID"  -O $OUTPUT_FILENAME;
rm -f /tmp/cookies.txt
