import argparse


def parse_config(argv=None):
    parser = argparse.ArgumentParser(description='ffmpeg configures')

    parser.add_argument('--dry_run', action='store_true',
                        help='only output command, not execute command')

    parser.add_argument('-i', '--input', type=str, default='in.mp4')

    parser.add_argument('-sp', '--split', default='(1,1)', type=str,
                        help='(A,B), A stands for the split number vertically on the width side' +
                        ', B stands for the split number horizontally on the height side')

    # parser.add_argument('--res', type=list, default=[360, 480, 720, 1080, 4000])

    parser.add_argument('-o', '--out_dir', type=str, default='outputs')

    parser.add_argument('-cd', '--crop_dir', type=str, default='crop_outputs')

    parser.add_argument('-cs', '--chunk_size', type=float,
                        default=4, help='unit: mb')

    parser.add_argument('-2', '--2pass', action='store_true')

    args = vars(parser.parse_args())
    args['split'] = args['split'].replace(' ', '')
    split = args['split'][1:-1].split(',')
    args['split'] = (int(split[0]), int(split[1]))

    return args
