#!/usr/bin/env python3
"""
使用 GitHub API 上传文件到仓库
使用前请设置环境变量: export GITHUB_TOKEN=your_token
"""
import os
import base64
import json
import urllib.request
from pathlib import Path

# 从环境变量获取令牌
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("错误: 请先设置环境变量 GITHUB_TOKEN")
    print("Windows: set GITHUB_TOKEN=your_token")
    print("Linux/Mac: export GITHUB_TOKEN=your_token")
    exit(1)

# 配置
REPO_OWNER = "YINLANB"
REPO_NAME = "cuddly-parakeet"
API_BASE = "https://api.github.com"

# 要上传的文件扩展名
INCLUDE_EXTENSIONS = {".py", ".md", ".txt", ".toml", ".html", ".css", ".js", ".bat", ".pyw"}

# 要排除的目录
EXCLUDE_DIRS = {"__pycache__", ".git", "venv", ".venv", "uploads", "processed", "weights", ".pytest_cache", ".claude"}

def create_headers():
    """创建请求头"""
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }

def get_file_content(file_path):
    """读取文件内容并编码"""
    with open(file_path, "rb") as f:
        content = f.read()
    return base64.b64encode(content).decode("utf-8")

def upload_file(file_path, commit_message="Upload file"):
    """上传单个文件"""
    rel_path = os.path.relpath(file_path, ".").replace("\\", "/")
    content = get_file_content(file_path)

    # 检查文件是否已存在
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{rel_path}"
    headers = create_headers()

    # 获取文件 SHA（如果存在）
    sha = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            sha = data.get("sha")
    except Exception:
        pass

    # 准备上传数据
    data = {
        "message": commit_message,
        "content": content
    }
    if sha:
        data["sha"] = sha

    # 上传文件
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="PUT"
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print(f"  [OK] {rel_path}")
            return True
    except Exception as e:
        print(f"  [ERROR] {rel_path}: {e}")
        return False

def collect_files():
    """收集要上传的文件"""
    files = []
    for root, dirs, filenames in os.walk("."):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for filename in filenames:
            file_path = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()

            # 检查扩展名
            if ext in INCLUDE_EXTENSIONS or filename in ["requirements.txt", "LICENSE", ".gitignore"]:
                files.append(file_path)

    return files

def main():
    """主函数"""
    print("=" * 60)
    print("  上传文件到 GitHub")
    print(f"  仓库: {REPO_OWNER}/{REPO_NAME}")
    print("=" * 60)
    print()

    # 收集文件
    print("收集文件...")
    files = collect_files()
    print(f"找到 {len(files)} 个文件")
    print()

    # 上传文件
    print("开始上传...")
    success_count = 0
    fail_count = 0

    for file_path in files:
        if upload_file(file_path, "Initial release: AI Mosaic Removal Tool v1.0.0"):
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 60)
    print(f"上传完成: 成功 {success_count}, 失败 {fail_count}")
    print(f"仓库地址: https://github.com/{REPO_OWNER}/{REPO_NAME}")
    print("=" * 60)

if __name__ == "__main__":
    main()
