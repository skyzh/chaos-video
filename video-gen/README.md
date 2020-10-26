# video-gen

Video-gen 负责将已有的视频文件转换为可以分块传输的形式。

Video-gen 除了能将视频切分为长度相近的块以外，还可以将画面横向切分。
通过设置不同分块的清晰度，客户端可以实现视频码率的多级动态变化。

## manifest

对于一个视频文件，video-gen 首先需要生成一个 manifest 文件，含有该视频对应的分块信息。
下面是一个例子。

```json
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

```json
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

## chunk 分割

video-gen 会将视频切成许多 chunk。在最高清晰度下，每个 chunk 大小应当在 4MB 左右。

音频、视频 chunk 一一对应。视频的第 i 个 chunk 对应音频的第 i 个 chunk。

不同清晰度视频的 chunk 一一对应。4K 的第 i 的 chunk 包含的帧范围和 360p 的第 i 个 chunk 一一对应。
