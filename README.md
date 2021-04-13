# Chaos Video

Chaos-Video 将视频空间切分，并将这些空间分块以不同码率传输，通过统一的
ABR 控制器 Multi-ABR 协同工作，从而解决ABR 算法受码率档位限制的问题。

详情可以参阅 slides.pdf 和 report.pdf。

## Architecture Overview

```plain
video-player <---> chaos-proxy <---> blank-server <---> video-gen 生成的视频分块
```

## Usage

首先，需要在本地准备一段测试视频和 Python, Node.js 环境。

使用 `video-gen` 生成测试视频。

```bash
cd video-gen
pip install -r requirements.txt
python main.py -i zelda_trailer.mp4 -sp "(1,4)" -o zelda -cd zelda-crop
```

而后，将视频文件拷贝到前端的 `public/data/` 目录下，编译 video-player 的前端文件。
编译前，需要调整 `App.js` 的参数（比如帧率和视频文件位置）。

```bash
cd video-player
npm i
npm run build
```

理论上，目录中应该有这些文件。

```plain
.
├── README.md
├── build
│   ├── asset-manifest.json
│   ├── data
│   │   ├── manifest.json
│   │   ├── zelda
│   │   │   ├── chunk_0_0
│   │   │   │   ├── zelda_trailer_c_0_0.mp4_1000.m3u8
                    ...
│   │   │       └── zelda_trailer_c_0_3.mp4_master.m3u8
│   │   └── zelda-crop
│   │       ├── zelda_trailer_c_0_0.mp4
│   │       ├── zelda_trailer_c_0_1.mp4
│   │       ├── zelda_trailer_c_0_2.mp4
│   │       └── zelda_trailer_c_0_3.mp4
│   ├── index.html
│   ├── robots.txt
│   └── static
│       ├── css
│       │   ├── main.d5ebe71c.chunk.css
│       │   └── main.d5ebe71c.chunk.css.map
│       └── js
│           ├── 2.3cdf8e33.chunk.js
│           ├── 2.3cdf8e33.chunk.js.LICENSE.txt
│           ├── 2.3cdf8e33.chunk.js.map
│           ├── main.623b8678.chunk.js
│           ├── main.623b8678.chunk.js.map
│           ├── runtime-main.dd450042.js
│           └── runtime-main.dd450042.js.map
├── package-lock.json
├── package.json
├── public
│   ├── data
│   │   ├── manifest.json
│   │   ├── zelda
│   │   │   ├── chunk_0_0
│   │   │   │   ├── zelda_trailer_c_0_0.mp4_1000.m3u8
│   │   │   │   ├── zelda_trailer_c_0_0.mp4_1000_00000.ts
                    ...
│   │   │       └── zelda_trailer_c_0_3.mp4_master.m3u8
│   │   └── zelda-crop
│   │       ├── zelda_trailer_c_0_0.mp4
│   │       ├── zelda_trailer_c_0_1.mp4
│   │       ├── zelda_trailer_c_0_2.mp4
│   │       └── zelda_trailer_c_0_3.mp4
│   ├── index.html
│   └── robots.txt
├── result
├── src
│   ├── AbrController.js
│   ├── App.js
│   ├── App.scss
│   ├── EWMA.ts
│   ├── EwmaBandWidthEstimator.ts
│   ├── index.js
│   ├── index.scss
│   ├── react-app-env.d.ts
│   ├── streamChart.js
│   ├── useForceUpdate.js
│   └── utils.ts
└── tsconfig.json

20 directories, 920 files
```

最后，通过 docker-compose 一键启动所有服务，即可测试。

```bash
docker-compose up -d --build
```

## Development Guide

* 先使用 venv 在项目目录里创建一个 virtual environment `python3 -m venv .venv`
* 而后激活虚拟环境 `source .venv/bin/activate` (Windows 可能要使用其他方法)
* 安装依赖 `pip install -r requirements.txt`
* 此时 VSCode 应该可以自动识别到虚拟环境，在开发过程中自动使用虚拟环境中的 Python。
* 开始开发 `git checkout -b some-new-feature`
* 测试 `make test`
* 格式化代码 `make format`
* 检查 warning `make lint`
* 发 PR
  * `git add -A`
  * `git commit -m "module: what have you done"`
  * `git push origin HEAD -u`
  * 在 GitHub 网页端发 PR
* PR 合并后，`git checkout master && git pull`，更新本地 master 分支。
