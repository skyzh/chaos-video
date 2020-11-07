#!/bin/bash

ffmpeg -i video.mkv -profile:v baseline -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8
