from arg_parser import parse_config
from bitrate_ladder import calc_video_config
from utils import split_chunks, concat_arg, write_json, \
    get_crop_path, get_input_info
import subprocess as sp
# I am so vegatable (((


if __name__ == "__main__":
    cfg = parse_config()
    input_n = cfg['input']

    in_info = get_input_info(input_n)
    cfg.update(in_info)

    my_ladder = calc_video_config(in_info['bit_rate'], in_info['width'], in_info['height'],\
        in_info['duration'], cfg['split'], cfg['chunk_size'])

    split_chunks(cfg)

    split_mode = cfg['split']
    split_mode = int(split_mode[0]), int(split_mode[1])

    for i in range(split_mode[0]):
        for j in range(split_mode[1]):
            crop_place = get_crop_path(cfg, i, j)
            
            tmp_cfg = cfg.copy()
            tmp_cfg.update({'out_streams': my_ladder, 'in': crop_place})
            command = concat_arg(tmp_cfg, i, j)
            sp.check_output(command)
            #out_files.append(out_file)

    #write_json(cfg, out_files)
    
    print('SUCCESS')

