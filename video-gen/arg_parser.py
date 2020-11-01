import argparse

def parse_config(argv=None):
    parser = argparse.ArgumentParser(description='ffmpeg coefficients')

    parser.add_argument('--input', default='in.mp4')

    parser.add_argument('--mode', default='normal')

    #parser.add_argument('--audio_mode', default='128')

    args = parser.parse_args()
    return vars(args)
