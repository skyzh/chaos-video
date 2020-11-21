from arg_parser import parse_config
from bitrate_ladder import calc_video_config
from utils import split_chunks, concat_arg, \
    get_crop_path, get_input_info, write_json
import subprocess as sp
# I am so vegatable (((


if __name__ == "__main__":
    commands = []
    cfg = parse_config()
    input_n = cfg['input']
    is_dryrun = cfg['dry_run']

    in_info = get_input_info(input_n)
    cfg.update(in_info)

    my_ladder = calc_video_config(in_info['bit_rate'], in_info['width'], in_info['height'],
                                  in_info['duration'], cfg['split'], cfg['chunk_size'])

    commands += split_chunks(cfg, is_dryrun)

    split_mode = cfg['split']
    split_mode = int(split_mode[0]), int(split_mode[1])

    crop_files = []
    out_files = []
    for i in range(split_mode[0]):
        for j in range(split_mode[1]):
            crop_place = get_crop_path(cfg, i, j)
            crop_files.append(crop_place)

            tmp_cfg = cfg.copy()
            tmp_cfg.update({'out_streams': my_ladder, 'in': crop_place})
            command, out_file = concat_arg(tmp_cfg, i, j)

            if not is_dryrun:
                sp.check_output(command, shell=True)

            commands.append(command)
            out_files.append(out_file)

    with open('commands.txt', 'w') as f:
        for item in commands:
            f.write("%s\n" % item)

    # seems strange, because there is no output file now if in dry_run mode ...
    # But if in dry_run mode, just ignore it
    write_json(cfg, crop_files, out_files)

    print('SUCCESS')
