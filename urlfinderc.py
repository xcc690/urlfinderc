import os
import platform
import subprocess
import json
import argparse
from datetime import datetime
from rich.console import Console
from rich.progress import Progress
import re

DEFAULT_CONFIG_PATH = "config.json"

# 创建一个console实例来显示信息
console = Console()

def process_output_file(output_filename):
    """处理URLFinder生成的输出文件，并生成HTML文件"""
    try:
        # 读取JSON数据
        with open(output_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取 info 字段中的数据
        info_data = data.get('info', {})
        
        # 提取 url 字段中的数据，按照 Size 去重
        url_data = data.get('url', [])
        unique_urls = {}
        for entry in url_data:
            size = entry.get('Size')
            if size not in unique_urls:
                unique_urls[size] = {
                    'Url': entry.get('Url'),
                    'Status': entry.get('Status'),
                    'Size': size,
                    'Title': entry.get('Title')
                }
        
        # 提取去重后的 url 数据
        unique_url_list = list(unique_urls.values())

        # 生成HTML内容
        html_content = generate_html(info_data, unique_url_list)
        
        # 写入HTML文件
        output_html_filename = os.path.splitext(output_filename)[0] + '.html'
        with open(output_html_filename, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)
        
        # 完成处理
        console.print(f"\nHTML file saved to: {output_html_filename}", style="bold green")
    
    except Exception as e:
        console.print(f"Error processing output file {output_filename}: {e}", style="bold red")

def generate_html(info_data, unique_url_list):
    """使用jinja2模板生成HTML内容"""
    from jinja2 import Environment, FileSystemLoader

    # 配置Jinja2环境
    env = Environment(loader=FileSystemLoader(searchpath='./templates'))  # 配置模板路径
    template = env.get_template('template.html')  # 选择模板

    # 渲染模板并生成HTML
    html_content = template.render(info_data=info_data, unique_url_list=unique_url_list)
    return html_content

def execute_command(config_file, f_path):
    # 读取配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 获取当前操作系统
    current_os = platform.system().lower()
    
    # 获取URLFinder二进制路径
    if current_os == 'windows':
        Urlfinder_path = config.get("windows_path")
        http_exe = config.get("http_exe_windows")  # 从config获取Windows下http.exe路径
    elif current_os == 'linux':
        Urlfinder_path = config.get("linux_path")
        http_exe = config.get("http_exe_linux")  # 从config获取Linux下http.exe路径
    else:
        raise EnvironmentError("Unsupported OS")
    
    # 读取文件并检查URL
    with open(f_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # 如果文件中的每一行都包含http://或https://，直接执行URLFinder
    if all(re.search(r'http[s]?://', line) for line in lines):
        # 直接执行URLFinder
        #console.print(f"All lines contain URLs. Executing URLFinder on {f_path}.", style="bold yellow")
        output_dir = os.path.splitext(f_path)[0]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = os.path.join(output_dir, f"{timestamp}.json")
        
        # 构建URLFinder命令
        command = [
            Urlfinder_path,
            "-s", "all",
            "-m", "3",
            "-a", config.get("user_agent"),
            "-ff", f_path,  # 使用传递的文件路径作为-ff参数的值
            "-o", output_filename
        ]
        
        # 执行URLFinder命令
        execute_urlfinder(command, output_filename)
    else:
        # 有的行没有URL，先用 http.exe 处理
        output_dir = os.path.splitext(f_path)[0]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = os.path.join(output_dir, f"{timestamp}.txt")
        source_file = output_filename

        # 执行 http.exe 处理文件
        http_command = [http_exe, "-l", f_path, "-o", output_filename]
        execute_http(http_command, source_file)

        # 使用处理后的文件执行 URLFinder
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = os.path.join(output_dir, f"{timestamp}.json")
        
        # 构建URLFinder命令
        command = [
            Urlfinder_path,
            "-s", "all",
            "-m", "3",
            "-a", config.get("user_agent"),
            "-ff", source_file,  # 使用处理后的文件
            "-o", output_filename
        ]
        
        # 执行URLFinder命令
        execute_urlfinder(command, output_filename)

def execute_http(command, source_file):
    """执行 http.exe 并检查结果"""
    try:
        # 确保路径是正确的，并替换掉反斜杠
        command[1] = os.path.normpath(command[1])  # 将相对路径转换为正确的格式
        
        # 打印最终执行的命令
        #console.print(f"Executing http command: {command}", style="bold yellow")  # 打印命令行
        
        # 使用 subprocess 执行命令并重定向输出
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(command, stdout=devnull, stderr=devnull)  # 将输出重定向到 DEVNULL

        #console.print(f"Processed source file saved to {source_file}", style="bold green")
    except subprocess.CalledProcessError as e:
        console.print(f"Error executing http.exe: {e}", style="bold red")


def execute_urlfinder(command, output_filename):
    """执行URLFinder命令并处理输出文件"""
    try:
        # 启动 URLFinder 进程，直接打印标准输出和标准错误
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, encoding='utf-8')
        
        # 正则表达式：匹配包含 "Validate" 和百分比的行
        validate_pattern = re.compile(r"Validate (\d+)%")

        # 创建进度条
        with Progress() as progress:
            task = progress.add_task("Validating...", total=100)
            
            # 只打印符合正则表达式的输出
            for line in process.stdout:
                match = validate_pattern.search(line)  # 查找匹配的模式
                if match:
                    # 获取百分比并更新进度条
                    percentage = int(match.group(1))
                    progress.update(task, completed=percentage)

        # 等待进程结束
        process.wait()

        # 如果命令执行成功
        if process.returncode == 0:
            console.print(f"\nCommand executed successfully.", style="bold green")
            # 处理URLFinder生成的输出文件并生成HTML
            process_output_file(output_filename)
        else:
            console.print(f"\nCommand failed with return code {process.returncode}", style="bold red")
    
    except subprocess.CalledProcessError as e:
        console.print(f"\nError executing command: {e}", style="bold red")
        console.print(f"stderr: {e.stderr}", style="bold red")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Execute URLFinder with specified options.")
    parser.add_argument('-f', type=str, help="File path for the -ff parameters.")
    parser.add_argument('-c', type=str, nargs='?', default=DEFAULT_CONFIG_PATH, help="Path to the config.json file. (default: config.json)")

    args = parser.parse_args()

    # 调用execute_command函数
    execute_command(args.c, args.f)
