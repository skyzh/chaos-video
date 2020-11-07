# Chaos Video

## Architecture Overview

```plain
video-player <---> chaos-proxy <---> blank-server <---> video-gen 生成的视频分块
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

## Usage

通过 `runserver.py` 同时启动 chaos-proxy, blank-server, 以及前端 (TBD)。
