import argparse


def parse_config(argv=None):
    parser = argparse.ArgumentParser(description='ffmpeg configures')

    parser.add_argument('--input', type=str, default='in.mp4')

    parser.add_argument('--split', default='(1,1)', help='(A,B), A stands for the split number vertically on the width side' +
        ', B stands for the split number horizontally on the height side')

    # parser.add_argument('--res', type=list, default=[360, 480, 720, 1080, 4000])

    parser.add_argument('--out_dir', default='outputs')

    parser.add_argument('--crop_dir', default='crop_outputs')

    parser.add_argument('--chunk_size', default=4, help='unit: mb')

    parser.add_argument('--2pass', default=False)

    args = vars(parser.parse_args())
    split = args['split'][1:-1].split(',')
    args['split'] = (int(split[0]), int(split[1]))
    return args
