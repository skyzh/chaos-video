import copy

# for H.264, the ladder roughly follows the standard of apple Inc.
default_ladder = [
    # format: bitrate (unit: kbps), width, height
    [145, 416, 234],    # 0
    [365, 480, 270],    # 1
    [730, 640, 360],    # 2
    [1100, 768, 432],   # 3
    [2000, 960, 540],   # 4
    [3000, 1280, 720],  # 5
    [4500, 1920, 1080],  # 6
    [6000, 1920, 1080],  # 7
    [7800, 1920, 1080]  # 8
]


def calc_video_config(inp_bitrate, inp_width, inp_height, inp_t_length, split_mode, chunk_size):
    # may be some problems, because when we split a video into several parts, then
    # the compression rate may suffer some loss, and the bitrate ladder may become inaccurate
    # return my_ladder with format [[bitrate, width, height, seconds], [...], ...]

    idx = 8
    # only maintain or reduce the bitrate, never increase bitrate
    for i, item in enumerate(default_ladder):
        if item[0] * 1e3 > inp_bitrate:
            idx = i
            break

    my_ladder = copy.deepcopy(default_ladder[:idx])

    if inp_bitrate != my_ladder[-1] * 1e3:
        tmp = [inp_bitrate/1000, 1920, 1080]
        my_ladder.append(tmp)

    split_mode = int(split_mode[0]), int(split_mode[1])
    split_number = split_mode[0] * split_mode[1]

    for i in range(len(my_ladder)):
        # chunk_size has the unit of MB
        seconds = min(chunk_size * 8e3 / my_ladder[-1][0], inp_t_length)
        my_ladder[i].append(seconds)
        # bitrate of each chunk after crop
        my_ladder[i][0] = my_ladder[i][0] / split_number
        if split_number > 1:
            my_ladder[i][0] = my_ladder[i][0] * 1.1
        # change resolution to that after crop and maximal resolution is input resolution
        if my_ladder[i][1] > inp_width or my_ladder[i][2] > inp_height:
            my_ladder[i][1] = -1
            my_ladder[i][2] = -1
        else:
            my_ladder[i][1] = my_ladder[i][1] / split_mode[0]
            my_ladder[i][2] = my_ladder[i][2] / split_mode[1]

    print('My bitrate ladder: ', my_ladder)
    return my_ladder
