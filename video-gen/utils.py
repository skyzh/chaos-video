import json
import os
import pprint

def concat_arg(args):
    command = 'ffmpeg '
    #keys = args.keys()
    #if 'input' in args:
    input = args['input']
    command += f"-i {input} "

    if 'res' in args:
        res = args['res']
        command += f'-vf scale=-2:{res},setsar=1:1 '
    if 'codec_v' in args:
        codec_v = args['codec_v']
        command += f'-c:v {codec_v} '
    if 'bitrate_v' in args:
        bitrate_v = args['bitrate_v']
        command += f'-b:v {bitrate_v} '
    if 'codec_a' in args:
        codec_a = args['codec_a']
        command += f'-c:a {codec_a} '
    if 'bitrate_a' in args:
        bitrate_a = args['bitrate_a']
        command += f'-b:a {bitrate_a} '
    if 'is_copy' in args and args['is_copy']:
        command += '-c copy '
        
    output = args['output']
    command += f'{output}'
    return command


def get_path(r_dir, quality, seq, format='mp4'):
    directory = os.path.join(r_dir, f'{quality}')
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(r_dir, f'{quality}', f'chunck-{seq}.{format}')


def get_path_from_cfg(cfg):
    r_dir = cfg['r_dir']
    quality = cfg['quality']
    seq = cfg['seq']
    fformat = cfg['format']
    return get_path(r_dir, quality, seq, fformat)


def write_json(cfgs, info, out_v_paths, out_a_paths):
    #print(info.keys())
    streams =  info['streams']
    formats = info['format']
    fps = streams[0]['r_frame_rate'].split('/')
    fps = int(fps[0]) / int(fps[1])
    total_frames = streams[0]['nb_frames']

    # previous intended to write otherwise, may change later
    v_paths = [
        item for item in out_v_paths
    ]

    a_paths = [
        item for item in out_a_paths
    ]

    if cfgs['mode'] == 'normal':
        out = {'name': formats['filename'], 
            'fps': fps,
            'total_frames': total_frames,
            'video': {"path": v_paths},
            'audio': {"path": a_paths}
        } 

    elif cfgs['mode'] == 'vertical-4':
        # has not finished
        out = {'name': formats['filename'], 
            'fps': fps,
            'total_frames': total_frames,
            'video': {"path": v_paths},
            'audio': {"path": a_paths},
            'chunks': []
        } 

    with open('manifest.json', 'w') as f:
        json.dump(out, f)
