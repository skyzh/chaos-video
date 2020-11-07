import copy

# for H.264, the ladder roughly follows the standard of apple Inc.
default_ladder = [
    # format: bitrate, width, height
    # [100, 300, 200],
    [145, 416, 234],    # 0
    [365, 480, 270],    # 1
    [730, 640, 360],    # 2
    [1100, 768, 432],   # 3
    [2000, 960, 540],   # 4
    [3000, 1280, 720],  # 5
    [4500, 1920, 1080], # 6
    [6000, 1920, 1080], # 7
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
    split_mode = int(split_mode[0]), int(split_mode[1])
    split_number = split_mode[0] * split_mode[1]

    for i in range(idx):
        seconds = min(chunk_size * 8e6 / my_ladder[-1][0], inp_t_length) # chunk_size has the unit of MB
        my_ladder[i].append(seconds)
        my_ladder[i][0] = my_ladder[i][0] / split_number # bitrate of each chunk after crop
        # change resolution to that after crop
        if my_ladder[i][1] > inp_width:
            # maximal resolution is input resolution ? if not necessary, we can just delete the code block
            my_ladder[i][1] = -1
            my_ladder[i][2] = -1
        else:
            my_ladder[i][1] = my_ladder[i][1] / split_mode[0]
            my_ladder[i][2] = my_ladder[i][1] / split_mode[1]
    
    print(my_ladder)
    return my_ladder
        

