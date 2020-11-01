import os
from arg_parser import parse_config
from utils import concat_arg, write_json, get_path
import subprocess as sp
import shlex as sx
import ffmpeg 
# Find fmpeg a useful package, but still not implement all with the package
# TODO: 1. implement all commands with ffmpeg-python package 2. find a way to best split chunks
# The formatted string f'{} seems only supported by python >= 3.6


if __name__ == "__main__":
    cfg = parse_config()
    #v_mode = cfg['video_mode']
    #a_mode = cfg['audio_mode']
    mode = cfg['mode']
    input_n = cfg['input']
    v_r_dir = 'video'
    a_r_dir = 'audio'

    #resolutions = ["360", "480", "720", "1080", "4000"]
    resolutions = ["60", "120", "240", "720"]

    in_info = ffmpeg.probe(f'{input_n}')

    out_v_paths = []
    out_a_paths = [] # record chunked video and audio paths
    for i in range(3):
        for j in range(2):
            # 0 for video, 1 for audio
            arg = {}
            my_info = {}

            arg['input'] = input_n
            #arg['codec_v'] = 'libx264'
            #arg['codec_a'] = 'aac'
            #arg['bitrate_v'] = str(5 * (i+1)) + 'k'
            #arg['bitrate_a'] = '10k'
            if j == 0:
                arg['res'] = resolutions[i]
                out = get_path(v_r_dir, arg['res'], seq=0)
                arg['is_copy'] = False
                out_v_paths.append(out)
            else:
                out = get_path(a_r_dir, resolutions[i], seq=0, format='aac')
                arg['is_copy'] = True
                out_a_paths.append(out)
                
            arg['output'] = out

            command = concat_arg(arg)
            #print(command)
            #os.system(command)
            sp.check_output(command)

    write_json(cfg, in_info, out_v_paths, out_a_paths)