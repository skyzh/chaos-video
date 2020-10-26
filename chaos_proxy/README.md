# chaos-proxy

Chaos proxy 是一个带延迟和限速的 HTTP 服务器。

```bash
pip install -r requirements.txt
python main.py                      # 启动服务器
python config.py latency 200        # 实时更改服务器参数
```

## Features

Chaos proxy 可以模拟各种网络环境。网络环境可以通过 `python config.py mode <mode>` 配置。

### Simple Mode

Simple mode 是默认模式。可以使用 `python config.py mode simple` 设置。进入 simple mode
后，用户可以设置如下参数。

* `latency` HTTP 链接首字节传输的延迟。以毫秒表示。
* `speed` 所有通过 chaos-proxy 的 HTTP 链接总速率限制。以字节数表示。

### Advanced Mode

Advanced mode 会引入随机的延迟、速率限制和抖动。

* `latency-(min|max)` HTTP 链接首字节传输的延迟。以毫秒表示。
* `speed-(min|max)` 所有通过 chaos-proxy 的 HTTP 链接总速率限制。以字节数表示。
* `jitter-prob` 抖动发生的概率。
* `jitter-(min|max)` 抖动（短时间断网）的时间长度。以毫秒表示。
* `reset-enable` 启用主动断开 HTTP 链接（模拟断网）。
* `reset-prob` 断网发生的概率。

### Pre-configured mode

Chaos-proxy 可以模拟各种网络环境。比如：

* `wifi`
* `5g`
* ...

这些预设模式基于 Advanced Mode，通过设置 Advanced Mode 的参数实现。
