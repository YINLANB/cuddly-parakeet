#!/usr/bin/env python3
"""
模型权重下载脚本
自动下载 Real-ESRGAN 和 GFPGAN 的预训练模型
"""
import os
import urllib.request
from pathlib import Path

# 模型权重配置
WEIGHTS_DIR = Path(__file__).parent / "weights"
WEIGHTS_DIR.mkdir(exist_ok=True)

MODELS = {
    "RealESRGAN_x4plus.pth": {
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x4plus.pth",
        "description": "Real-ESRGAN 通用超分辨率模型 (4x放大)"
    },
    "GFPGANv1.4.pth": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
        "description": "GFPGAN 人脸恢复模型"
    },
    "RealESRGAN_x4plus_anime_6B.pth": {
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
        "description": "Real-ESRGAN 动漫/插画专用模型 (4x放大)"
    }
}


def download_model(name: str, info: dict) -> bool:
    """
    下载单个模型

    Args:
        name: 模型文件名
        info: 模型信息

    Returns:
        是否下载成功
    """
    filepath = WEIGHTS_DIR / name

    if filepath.exists():
        print(f"[SKIP] {name} 已存在")
        return True

    print(f"\n[DOWNLOAD] {info['description']}")
    print(f"[URL] {info['url']}")
    print(f"[SIZE] 正在下载...")

    try:
        # 显示下载进度
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r[PROGRESS] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="", flush=True)

        urllib.request.urlretrieve(info['url'], str(filepath), progress_hook)
        print(f"\n[OK] {name} 下载完成")
        return True

    except Exception as e:
        print(f"\n[ERROR] {name} 下载失败: {e}")
        if filepath.exists():
            filepath.unlink()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("马赛克去除工具 - 模型权重下载脚本")
    print("=" * 60)
    print(f"\n下载目录: {WEIGHTS_DIR}\n")

    success_count = 0
    total_count = len(MODELS)

    for name, info in MODELS.items():
        if download_model(name, info):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"下载完成: {success_count}/{total_count} 个模型")
    print("=" * 60)

    if success_count == total_count:
        print("\n所有模型下载完成！可以启动应用了。")
        print("运行命令: python -m uvicorn app.main:app --reload")
    else:
        print("\n部分模型下载失败，请检查网络连接后重试。")


if __name__ == "__main__":
    main()
