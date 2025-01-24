# URLFinder 自动化工具

这是一个基于 Python 的自动化工具，用于处理 URL 文件，执行 `URLFinder`，并根据结果生成 HTML 报告。它还支持在输入文件包含非 URL 内容的情况下，使用辅助工具 `httpx` 进行预处理。

## 功能特点

- 自动使用 `URLFinder` 处理 URL 文件。
- 针对非 URL 文件内容，支持通过 `httpx` 进行预处理。
- 生成包含唯一 URL 和元数据信息的 JSON 和 HTML 报告。
- 根据输入文件名称自动创建输出目录。

## 运行环境要求

- Python 版本：3.8 或更高。
- 外部工具：
  - `URLFinder`（二进制可执行文件）
  - `httpx.exe`（二进制可执行文件，用于预处理）

## 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/urlfinder-automation.git
cd urlfinder-automation
```
2. 安装依赖库：
```
pip install rich jinja2
```
3. 配置工具路径：创建一个 config.json 文件并设置 URLFinder 和 http.exe 的路径。
配置文件示例
在项目根目录下创建 config.json 文件，内容示例如下：
```json
{
  "windows_path": "path/to/urlfinder.exe",
  "linux_path": "/path/to/urlfinder",
  "http_exe_windows": "path/to/http.exe",
  "http_exe_linux": "/path/to/http",
  "user_agent": "YourCustomUserAgent"
}
```

## 使用方法
1. 使用命令行运行工具：
```
python script.py -f <文件路径> [-c <配置文件路径>]
```

* -f：指定输入文件路径。
* -c：指定配置文件路径（可选，默认是 config.json）。
2. 工具会根据输入文件自动处理并生成以下内容：

* JSON 报告：存储处理结果的详细信息。
* HTML 报告：便于阅读的报告文件。
3. 输出的文件会保存在与输入文件同名的目录中。

示例
假设您的输入文件是 urls.txt，运行以下命令：

```
python script.py -f urls.txt
```

工具会自动生成以下目录和文件：

```php
urls/
├── <时间戳>.json
├── <时间戳>.html
```
## 常见问题
### 如果输入文件中包含非 URL 内容怎么办？
工具会自动调用 http.exe 对输入文件进行预处理，将非 URL 内容过滤或转换为可处理的格式。

### 不同操作系统是否支持？
工具支持 Windows 和 Linux 系统，并会根据当前操作系统自动选择正确的二进制文件路径。

## 贡献
欢迎提交 Issue 或 Pull Request 以改进本工具。
