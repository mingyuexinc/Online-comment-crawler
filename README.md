# Online-comment-crawler

A web crawler for Steam user game reviews (pure HTML). Fetches a single user's recommended reviews and writes each game's review text to a separate `.txt` file in a local folder.

## 安装

```bash
pip install -r requirements.txt
```

## 配置

参数通过 **配置文件** 传递。在项目根目录放置 `config.yaml`（或通过 `-c` 指定路径 / 环境变量 `STEAM_CONFIG` 指定路径）。输出目录 `output_dir` 支持 **相对路径** 和 **绝对路径**（如 `D:/steam_reviews`）。

编辑 `config.yaml` 示例：

```yaml
user_id: "valve"          # 自定义 ID 或 64 位 Steam ID
use_vanity: true          # true=自定义ID，false=64位Steam ID
output_dir: "data/reviews" # 支持绝对路径，如 D:/reviews
max_pages: 500
request_interval: 2.0
request_timeout: 15
request_retries: 3
```

## 运行

```bash
# 使用当前目录下的 config.yaml
py -m online_comment_crawler

# 指定配置文件路径
py -m online_comment_crawler -c D:/my_config.yaml

# 或运行脚本（需在项目根目录，或保证 config.yaml 在 cwd）
py scripts/run_single_user.py -c config.yaml
```

## 项目结构

- `config.yaml` – 配置文件（用户 ID、输出目录、请求参数等）
- `online_comment_crawler/` – 主包
- `scripts/run_single_user.py` – CLI 入口
- 输出目录由 `output_dir` 指定，每个游戏一个 `<游戏名>.txt`
