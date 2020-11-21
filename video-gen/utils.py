import json
import os
import subprocess as sp
import ffmpeg


def split_chunks(cfg, is_dryrun=False):
    split_mode = cfg['split']
    split_mode = int(split_mode[0]), int(split_mode[1])

    input = cfg['input']
    width = int(cfg['width'])
    height = int(cfg['height'])
    v_interval = width // split_mode[1]
    h_interval = height // split_mode[0]
    commands = []
    for i in range(split_mode[0]):
        for j in range(split_mode[1]):
            start = h_interval * i, v_interval * j
            out_place = get_crop_path(cfg, i, j)

            command = f'ffmpeg -i {input} ' +\
                f'-filter:v \"crop={v_interval}:{h_interval}:{start[0]}:{start[1]}\" ' +\
                '-c:a copy ' +\
                f'{out_place}'

            commands.append(command)

            if not is_dryrun:
                sp.check_output(command)

    return commands


def concat_arg(args, i, j):
    input = args['in']
    seconds = args['out_streams'][0][3]
    out_dir = os.path.join(args['out_dir'], f'chunk_{i}_{j}')
    # use_2_pass = args['2pass']

    out_names = []
    bitrates_str = ''
    for item in args['out_streams']:
        bitrate = int(item[0])
        bitrates_str += f'{bitrate}'
        if item[1] > 0:
            width = int(item[1])
            height = int(item[2])
            bitrates_str += f'-{width}*{height}'
        bitrates_str += ','
        input_name = input.split('/')[-1]
        out_names.append(f'{input_name}_{bitrate}.m3u8')

    bitrates_str = bitrates_str[:-1]

    if args['2pass']:
        command = command = 'sh ./HLS-Stream-Creator.sh ' +\
            f'-i {input} ' +\
            f'-b {bitrates_str} ' +\
            f'-o {out_dir} ' +\
            '-2'
    else:
        command = 'sh ./HLS-Stream-Creator.sh ' +\
            f'-i {input} ' +\
            f'-s {seconds} ' +\
            f'-b {bitrates_str} ' +\
            f'-o {out_dir}'

    return command, out_names


def get_crop_path(cfg, i_idx, j_idx):
    input = cfg['input']
    inp_name = input.split('.')[0]
    inp_suffix = input.split('.')[-1]
    out_dir = cfg['crop_dir']

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # return os.path.join(out_dir, f'{inp_name}_c_{i_idx}_{j_idx}.{inp_suffix}')
    return out_dir + '/' + f'{inp_name}_c_{i_idx}_{j_idx}.{inp_suffix}'


def get_input_info(input_n):
    # get only the VIDEO information, do not mistake for VIDEO + AUDIO
    info = {}
    raw_info = ffmpeg.probe(input_n)
    streams_info = raw_info['streams']
    # format_info = raw_info['format']
    info['width'] = int(streams_info[0]['width'])
    info['height'] = int(streams_info[0]['height'])

    fps = streams_info[0]['r_frame_rate'].split('/')
    info['fps'] = int(fps[0]) / int(fps[1])

    info['total_frames'] = int(streams_info[0]['nb_frames'])
    info['duration'] = float(streams_info[0]['duration'])
    info['bit_rate'] = int(streams_info[0]['bit_rate'])

    return info


def write_json(cfg, crop_files, out_files):
    out = {
        # just the original file name, no suffix
        'name': cfg['input'].split('.')[0],
        'out_dir': cfg['out_dir'],
        'streams': {
            'original': cfg['input'],
            'original_crop': crop_files,
            'chunks': out_files
        }
    }

    with open('manifest.json', 'w') as f:
        json.dump(out, f)
