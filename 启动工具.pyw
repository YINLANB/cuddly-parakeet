"""
马赛克去除工具 - 启动器
双击此文件可自动启动服务器并打开浏览器
"""
import subprocess
import time
import webbrowser
import sys
import os

def main():
    print("=" * 50)
    print("    马赛克去除工具 - 启动中...")
    print("=" * 50)
    print()

    # 启动服务器
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    # 等待服务器启动
    print("正在启动服务器...")
    time.sleep(3)

    # 打开浏览器
    print("正在打开浏览器...")
    webbrowser.open("http://localhost:8000")

    print()
    print("✅ 服务器已启动！")
    print("✅ 浏览器已打开！")
    print()
    print("访问地址: http://localhost:8000")
    print()
    print("关闭此窗口或按 Ctrl+C 停止服务器")
    print()

    try:
        server.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.terminate()
        server.wait()
        print("服务器已停止")

if __name__ == "__main__":
    main()
