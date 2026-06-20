#!/usr/bin/env python3
"""
马赛克去除工具 - 启动脚本
"""
import uvicorn
from app.config import HOST, PORT


def main():
    """启动应用"""
    print("=" * 60)
    print("  马赛克去除工具 - Mosaic Removal Tool")
    print("=" * 60)
    print(f"\n启动服务器...")
    print(f"访问地址: http://localhost:{PORT}")
    print(f"API文档: http://localhost:{PORT}/docs")
    print("\n按 Ctrl+C 停止服务器\n")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
