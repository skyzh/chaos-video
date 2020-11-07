# video-gen

Video-gen 负责将已有的视频文件转换为可以分块传输的形式。

Video-gen 除了能将视频切分为长度相近的块以外，还可以将画面横向切分。
通过设置不同分块的清晰度，客户端可以实现视频码率的多级动态变化。

## HLS-based Streaming

Video-gen 将视频转换为 HLS 播放列表和视频分块。一个 HLS 播放列表中含有
多个码率（分辨率）的视频。

与此同时，为了实现视频码率的多级动态变化，Video-gen 会同时生成多个播放列表。
每个播放列表包含视频画面的一部分（纵向/横向/棋盘切割）。

## Usage


```bash
python main.py \
    -i or --input 'input file'\         # Input file
    -sp or --split '(A,B)'\             # split mode, A stands for the split number vertically on the width side, 
                                        # B stands for the split number horizontally on the height side
    -o or --out_dir 'output directory'\ # output directory
    -cd or --crop_dir 'crop video directory'\   # temporary directory for videos after crop(split)
    -cs or --chunk_size 'k'\            # the chunk size of maximal resolution, in the unit of MB
    --2pass                             # whether use 2 pass encoding, has not implemented now
```

## Example

```bash
python main.py \
    -i 'in.mp4'\
    -sp '(2,2)'\
    -o 'outputs'\
    -cd 'crop_outputs'
```

之后，可以生成 4 (分割) + 1 (原始) = 5 条 HLS 流。在此基础上，生成一个 manifest。

```json
{
    "name": "我的前半生 EP1",
    "streams": {
        "original": "original.m3u8",
        "vertical-4": "vertical-%d.m3u8"
    }
}
```

## Reference

* https://github.com/lebougui/hls-creator
* https://github.com/bentasker/HLS-Stream-Creator

## 弃用的方案

### manifest

对于一个视频文件，video-gen 首先需要生成一个 manifest 文件，含有该视频对应的分块信息。
下面是一个例子。

```js
{
    "name": "三十而已 EP01",
    "fps": 25,
    "total_frames": 2333333,
    "mode": "vertical-4", // 单画面纵向切割为 4 份
    "video": {
        "path": "videos/{quality}/chunk-{seq}-{split}.mp4",
        "mode": ["360p", "480p", "720p", "1080p", "4K"],     // 支持的分辨率，按数据量由低到高排序
    },
    "audio": {
        "path": "audios/{quality}/chunk-{seq}.m4a",
        "mode": ["128", "320"]
    },
    "chunks": [
        {
            "frame": 20,                    // 每一个 chunk 包含的帧数
            "priority": [4, 3, 2, 1]        // 清晰度切换优先级。这个例子里，如果需要切高清晰度，优先将最右边一块切换到高分。
        },
        ...
    ]
}
```

```js
{
    "name": "三十而已 EP02",
    "fps": 25,
    "total_frames": 2333333,
    "mode": "normal", // 仅提供不同清晰度，不划分画面
    "video": {
        "path": "videos/{quality}/chunk-{seq}.mp4"
    },
    "audio": {
        "path": "audios/{quality}/chunk-{seq}.m4a"
    }
}
```

由此可以产生如下的目录结构

```text
| manifest-mode-split.json # 单画面切割，一个视频可以有多个 manifest
| manifest.json            # 不切割
| videos
    | 360p
        | chunk-0001.mp4
        | chunk-0001-01.mp4
        | ...
    | 480p
        | ...
    | 720p
        | ...
    | 1080p
        | ...
    | 4K
        | ...
| audios
    | 128
        | chunk-0001.m4a
        | ...
    | 320
        | chunk-0001.m4a
        | ...
```

### chunk 分割

video-gen 会将视频切成许多 chunk。在最高清晰度下，每个 chunk 大小应当在 4MB 左右。

音频、视频 chunk 一一对应。视频的第 i 个 chunk 对应音频的第 i 个 chunk。

不同清晰度视频的 chunk 一一对应。4K 的第 i 的 chunk 包含的帧范围和 360p 的第 i 个 chunk 一一对应。
