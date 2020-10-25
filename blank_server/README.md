# blank-server

Blank server 具有两个功能。它可以将本地文件通过 HTTP 协议提供，也可以产生测试用的任意大小的空白文件。

```bash
pip install -r requirements.txt
python main.py
```

`main.py` 可以带参数。

* `--port 2333` 指定监听端口，默认 2333。
* `--static_path /path` 指定静态文件的路径，默认为 `blank-server/static/`。

而后，HTTP 服务器会在 2333 端口开启。可以通过下面几个 endpoint 访问数据。

* `/ping` 返回 "Hello, world"。
* `/static/*` 返回 `static_path` 目录下的文件。
* `/blank/<size>` 返回大小为 `size` 字节的空白文件。
